import os
import random
import pymysql
import certifi
from faker import Faker
from datetime import date, timedelta, datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

fake = Faker()

# --- CONFIGURATION ---
NUM_TEAMS = 24 
NUM_STADIUMS = 24
NUM_REFEREES = 40
PLAYERS_PER_TEAM = 12 
YEARS_TO_SIMULATE = [2021, 2022, 2023, 2024]

# Connect to Database
def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        port=4000,
        ssl={'ca': certifi.where()},
        autocommit=False 
    )

# --- GAMEPLAY SIMULATION ENGINE ---
def simulate_match_batch(cursor, matches_data, team_rosters, event_map):
    """
    Simulates a batch of matches.
    matches_data list of tuples: (match_id, home_id, away_id, match_date)
    Returns: {match_id: {'winner': team_id, 'loser': team_id, 'score': (h_pts, a_pts)}}
    """
    results = {}
    event_buffer = []
    
    for match_info in matches_data:
        m_id, home_id, away_id, m_date = match_info
        
        # Determine Game Start Time
        if isinstance(m_date, str):
            base_date = datetime.strptime(m_date, '%Y-%m-%d')
        else:
            base_date = datetime.combine(m_date, datetime.min.time())
            
        # Rosters Check
        if home_id not in team_rosters or away_id not in team_rosters:
            print(f"Skipping match {m_id} due to missing roster.")
            continue
        
        # UNPACK ROSTERS (Players vs Coaches)
        home_data = team_rosters[home_id]
        away_data = team_rosters[away_id]
        
        home_players = home_data['players'][:]
        away_players = away_data['players'][:]
        home_coaches = home_data['coaches'][:] 
        away_coaches = away_data['coaches'][:]
        
        # On Court / Bench (PLAYERS ONLY)
        on_court = { 'home': set(home_players[:5]), 'away': set(away_players[:5]) }
        bench = { 'home': list(home_players[5:]), 'away': list(away_players[5:]) }
        
        # Stats
        scores = {'home': 0, 'away': 0}
        player_fouls = {pid: 0 for pid in home_players + away_players}
        team_fouls = {'home': 0, 'away': 0}
        
        # Helper to log event
        def log(pid, evt, time):
            event_buffer.append((m_id, pid, event_map[evt], time))

        # --- QUARTERS LOOP ---
        for quarter in range(1, 5):
            team_fouls['home'] = 0
            team_fouls['away'] = 0
            current_time = base_date + timedelta(minutes=(quarter-1)*10)
            end_time = current_time + timedelta(minutes=10)
            
            # Possession
            possession = 'home' if quarter in [1, 4] else 'away'

            while current_time < end_time:
                time_used = random.randint(8, 24)
                current_time += timedelta(seconds=time_used)
                if current_time >= end_time: break

                atk = possession
                dfn = 'away' if atk == 'home' else 'home'
                
                attacker = random.choice(list(on_court[atk]))
                defender = random.choice(list(on_court[dfn]))
                
                outcome = random.random()
                
                # 1. Turnover
                if outcome < 0.15:
                    etype = random.choice(['Turnover', 'Steal', 'Time running out'])
                    if etype == 'Steal':
                        log(defender, 'Steal', current_time)
                        log(attacker, 'Turnover', current_time)
                    else:
                        log(attacker, etype, current_time)
                    possession = dfn 
                
                # 2. Foul
                elif outcome < 0.30:
                    ftype = random.choices(['Personal Foul', 'Offensive Foul', 'Technical Foul', 'Flagrant Foul'], weights=[70,15,10,5])[0]
                    
                    if ftype == 'Offensive Foul':
                        log(attacker, ftype, current_time)
                        player_fouls[attacker] += 1
                        team_fouls[atk] += 1
                        possession = dfn
                        if player_fouls[attacker] >= 5 and bench[atk]:
                            sub = bench[atk].pop(0)
                            on_court[atk].remove(attacker)
                            on_court[atk].add(sub)
                            log(attacker, 'Substitution', current_time)
                            log(sub, 'Substitution', current_time)
                            
                    elif ftype == 'Technical Foul':
                        is_coach_tech = random.random() < 0.30
                        target_side = random.choice([atk, dfn])
                        
                        if is_coach_tech:
                            coaches_list = home_coaches if target_side == 'home' else away_coaches
                            if coaches_list:
                                coach_id = random.choice(coaches_list)
                                log(coach_id, 'Technical Foul', current_time)
                        else:
                            p_target = random.choice(list(on_court[target_side]))
                            log(p_target, 'Technical Foul', current_time)
                            player_fouls[p_target] += 1
                        
                        shooter_side = 'away' if target_side == 'home' else 'home'
                        shooter = random.choice(list(on_court[shooter_side]))
                        res = random.choice(['Made', 'Attempt'])
                        log(shooter, f"Free Throw {res}", current_time)
                        if res == 'Made': scores[shooter_side] += 1

                    else: # Personal or Flagrant
                        log(defender, ftype, current_time)
                        player_fouls[defender] += 1
                        team_fouls[dfn] += 1
                        
                        shots = 0
                        if ftype == 'Flagrant Foul': shots = 2
                        elif team_fouls[dfn] > 4: shots = 2
                        
                        if shots > 0:
                            last_made = False
                            for s in range(shots):
                                res = random.choice(['Made', 'Attempt'])
                                log(attacker, f"Free Throw {res}", current_time)
                                if res == 'Made': 
                                    scores[atk] += 1
                                    last_made = True
                            
                            if last_made: possession = dfn
                            else:
                                if random.random() < 0.75:
                                    log(random.choice(list(on_court[dfn])), 'Defensive Rebound', current_time)
                                    possession = dfn
                                else:
                                    log(random.choice(list(on_court[atk])), 'Offensive Rebound', current_time)
                                    possession = atk
                        else:
                            possession = atk 
                            
                        if player_fouls[defender] >= 5 and bench[dfn]:
                            sub = bench[dfn].pop(0)
                            on_court[dfn].remove(defender)
                            on_court[dfn].add(sub)
                            log(defender, 'Substitution', current_time)
                            log(sub, 'Substitution', current_time)

                # 3. Shot
                else:
                    is_3pt = random.random() < 0.35
                    s_type = '3-Point Field Goal' if is_3pt else '2-Point Field Goal'
                    pts = 3 if is_3pt else 2
                    is_made = random.choice([True, False])
                    
                    if is_made:
                        teammate = random.choice(list(on_court[atk] - {attacker}))
                        log(teammate, 'Assist', current_time)
                        
                        log(attacker, f"{s_type} Made", current_time)
                        scores[atk] += pts
                        
                        if random.random() < 0.05:
                            log(defender, 'Personal Foul', current_time)
                            log(attacker, 'Free Throw Made', current_time)
                            scores[atk] += 1
                        
                        possession = dfn
                    else:
                        log(attacker, f"{s_type} Attempt", current_time)
                        if random.random() < 0.1: 
                            log(defender, 'Block', current_time)
                            log(random.choice(list(on_court[dfn])), 'Defensive Rebound', current_time)
                            possession = dfn
                        elif random.random() < 0.75:
                            log(random.choice(list(on_court[dfn])), 'Defensive Rebound', current_time)
                            possession = dfn
                        else:
                            log(random.choice(list(on_court[atk])), 'Offensive Rebound', current_time)
                            possession = atk 

                # Substitutions
                if random.random() < 0.04:
                    side = random.choice(['home', 'away'])
                    if bench[side]:
                        po = random.choice(list(on_court[side]))
                        pi = bench[side].pop(0)
                        bench[side].append(po)
                        on_court[side].remove(po)
                        on_court[side].add(pi)
                        log(po, 'Substitution', current_time)
                        log(pi, 'Substitution', current_time)

        while scores['home'] == scores['away']:
            scores[random.choice(['home', 'away'])] += 2
        
        winner = home_id if scores['home'] > scores['away'] else away_id
        loser = away_id if winner == home_id else home_id
        
        results[m_id] = {'winner': winner, 'loser': loser, 'score': scores}
    
    if event_buffer:
        cursor.executemany("INSERT INTO Event_Creation (match_id, person_id, event_id, game_time) VALUES (%s, %s, %s, %s)", event_buffer)
    
    return results

# --- TOURNAMENT MANAGER ---

def run_all_seasons(conn, cursor):
    print("--- STARTING MULTI-YEAR SIMULATION ---")
    
    # 1. Setup Static Data (Run Once)
    setup_static_data(conn, cursor)
    conn.commit()
    
    # 2. Prepare Shared Resources
    cursor.execute("SELECT id FROM Team")
    all_teams = [r[0] for r in cursor.fetchall()]
    teams_24 = all_teams[:24]
    
    cursor.execute("SELECT pt.team_id, pt.person_id, p.speciality FROM Person_Team pt JOIN Person p ON pt.person_id = p.id")
    rosters = {} 
    for t, p, spec in cursor.fetchall():
        if t not in rosters: rosters[t] = {'players': [], 'coaches': []}
        if spec == 'Coach': rosters[t]['coaches'].append(p)
        else: rosters[t]['players'].append(p)
        
    cursor.execute("SELECT name, id FROM Event")
    e_map = {r[0]: r[1] for r in cursor.fetchall()}
    
    cursor.execute("SELECT id FROM Stadium")
    stadiums = [r[0] for r in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM Referee")
    referees = [r[0] for r in cursor.fetchall()]
    
    team_home_stadiums = {}
    random.shuffle(stadiums)
    for i, tid in enumerate(teams_24):
        team_home_stadiums[tid] = stadiums[i % len(stadiums)]
    
    # 3. Iterate Years
    match_id_counter = 100000 # Base ID
    
    for year in YEARS_TO_SIMULATE:
        # Update counter to be year-prefixed for clarity (e.g., 20210000)
        match_id_counter = year * 10000 
        print(f"\n>>> STARTING SEASON {year} <<<")
        simulate_season(conn, cursor, year, match_id_counter, teams_24, rosters, e_map, team_home_stadiums, referees)
        conn.commit()

def simulate_season(conn, cursor, year, match_id_start, teams, rosters, e_map, home_stadiums, referees):
    # --- HIERARCHY FOR YEAR ---
    cursor.execute("INSERT IGNORE INTO Season (year) VALUES (%s)", (year,))
    
    # Create Phases for THIS year (Auto-Inc ID)
    # Phase 1: Groups, Phase 2: Finals
    # We need to map logical_phase_id (1,2) -> actual_db_id
    phase_db_map = {} # {1: db_id, 2: db_id}
    
    for logical_p in [1, 2]:
        cursor.execute("INSERT INTO Phase (phase_id, year) VALUES (%s, %s)", (logical_p, year))
        phase_db_map[logical_p] = cursor.lastrowid
        
    # Create Rounds linked to these Phases
    phase_rounds_map = {} # {logical_phase: [round_db_ids]}
    rounds_config = {1: 5, 2: 4} # 5 rounds in groups, 4 in finals
    
    for log_p, count in rounds_config.items():
        phase_pk = phase_db_map[log_p]
        phase_rounds_map[log_p] = []
        for r_num in range(1, count + 1):
            cursor.execute("INSERT INTO `Round` (round_id, phase_id) VALUES (%s, %s)", (r_num, phase_pk))
            phase_rounds_map[log_p].append(cursor.lastrowid)
            
    match_id_counter = match_id_start
    start_date = date(year, 10, 1)
    
    # Link Helper
    team_stadium_buffer = []
    match_referee_buffer = []
    
    def link_match(mid, hid, aid, sid, rid):
        for ref in random.sample(referees, 3):
            match_referee_buffer.append((mid, ref))
        team_stadium_buffer.append((hid, sid, rid))
        team_stadium_buffer.append((aid, sid, rid))

    # --- PHASE 1: GROUPS ---
    random.shuffle(teams)
    groups = [teams[i:i+6] for i in range(0, 24, 6)]
    group_standings = {t: 0 for t in teams}
    p1_matches = []
    
    for group in groups:
        schedule = generate_single_rr(group)
        for r_idx, round_matches in enumerate(schedule):
            curr_round_pk = phase_rounds_map[1][r_idx]
            mdate = start_date + timedelta(weeks=r_idx)
            
            for h, a in round_matches:
                mid = match_id_counter; match_id_counter += 1
                stad = home_stadiums[h]
                p1_matches.append((mid, h, a, mdate))
                cursor.execute("INSERT INTO `Match` (id, match_date, status, round_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', %s, %s, %s, %s)", (mid, mdate, curr_round_pk, stad, h, a))
                link_match(mid, h, a, stad, curr_round_pk)
    
    conn.commit()
    res_p1 = simulate_match_batch(cursor, p1_matches, rosters, e_map)
    for res in res_p1.values(): group_standings[res['winner']] += 1
    
    qualifiers = []
    for g in groups:
        qualifiers.extend(sorted(g, key=lambda t: group_standings[t], reverse=True)[:4])
        
    print(f"   -> Group Stage Complete. {len(qualifiers)} teams qualified.")
    
    # --- PHASE 2: FINALS ---
    p2_round_ids = phase_rounds_map[2]
    current_teams = qualifiers
    random.shuffle(current_teams)
    curr_date = start_date + timedelta(weeks=10)
    
    # R16
    r16_matches = []
    for i in range(0, 16, 2):
        h, a = current_teams[i], current_teams[i+1]
        mid = match_id_counter; match_id_counter += 1
        st = home_stadiums[h]
        r16_matches.append((mid, h, a, curr_date))
        cursor.execute("INSERT INTO `Match` (id, match_date, status, round_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', %s, %s, %s, %s)", (mid, curr_date, p2_round_ids[0], st, h, a))
        link_match(mid, h, a, st, p2_round_ids[0])
        
    conn.commit()
    r16_res = simulate_match_batch(cursor, r16_matches, rosters, e_map)
    qf_teams = [r16_res[m[0]]['winner'] for m in r16_matches]
    
    # QF
    qf_matches = []
    curr_date += timedelta(days=7)
    for i in range(0, 8, 2):
        h, a = qf_teams[i], qf_teams[i+1]
        mid = match_id_counter; match_id_counter += 1
        st = home_stadiums[h]
        qf_matches.append((mid, h, a, curr_date))
        cursor.execute("INSERT INTO `Match` (id, match_date, status, round_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', %s, %s, %s, %s)", (mid, curr_date, p2_round_ids[1], st, h, a))
        link_match(mid, h, a, st, p2_round_ids[1])
        
    conn.commit()
    qf_res = simulate_match_batch(cursor, qf_matches, rosters, e_map)
    sf_teams = [qf_res[m[0]]['winner'] for m in qf_matches]
    
    # SF
    sf_matches = []
    curr_date += timedelta(days=7)
    mid1 = match_id_counter; match_id_counter += 1
    st1 = home_stadiums[sf_teams[0]]
    sf_matches.append((mid1, sf_teams[0], sf_teams[1], curr_date))
    cursor.execute("INSERT INTO `Match` (id, match_date, status, round_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', %s, %s, %s, %s)", (mid1, curr_date, p2_round_ids[2], st1, sf_teams[0], sf_teams[1]))
    link_match(mid1, sf_teams[0], sf_teams[1], st1, p2_round_ids[2])
    
    mid2 = match_id_counter; match_id_counter += 1
    st2 = home_stadiums[sf_teams[2]]
    sf_matches.append((mid2, sf_teams[2], sf_teams[3], curr_date))
    cursor.execute("INSERT INTO `Match` (id, match_date, status, round_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', %s, %s, %s, %s)", (mid2, curr_date, p2_round_ids[2], st2, sf_teams[2], sf_teams[3]))
    link_match(mid2, sf_teams[2], sf_teams[3], st2, p2_round_ids[2])
    
    conn.commit()
    sf_res = simulate_match_batch(cursor, sf_matches, rosters, e_map)
    
    fin_teams = []
    third_teams = []
    for m in sf_matches:
        fin_teams.append(sf_res[m[0]]['winner'])
        third_teams.append(sf_res[m[0]]['loser'])
        
    # FINALS
    fin_matches = []
    curr_date += timedelta(days=2)
    # 3rd
    mid3 = match_id_counter; match_id_counter += 1
    st3 = home_stadiums[third_teams[0]]
    fin_matches.append((mid3, third_teams[0], third_teams[1], curr_date))
    cursor.execute("INSERT INTO `Match` (id, match_date, status, round_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', %s, %s, %s, %s)", (mid3, curr_date, p2_round_ids[3], st3, third_teams[0], third_teams[1]))
    link_match(mid3, third_teams[0], third_teams[1], st3, p2_round_ids[3])
    
    # Champ
    midF = match_id_counter; match_id_counter += 1
    stF = home_stadiums[fin_teams[0]]
    fin_matches.append((midF, fin_teams[0], fin_teams[1], curr_date))
    cursor.execute("INSERT INTO `Match` (id, match_date, status, round_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', %s, %s, %s, %s)", (midF, curr_date, p2_round_ids[3], stF, fin_teams[0], fin_teams[1]))
    link_match(midF, fin_teams[0], fin_teams[1], stF, p2_round_ids[3])
    
    conn.commit()
    fin_res = simulate_match_batch(cursor, fin_matches, rosters, e_map)
    
    # COMMIT LINKS
    if match_referee_buffer:
        cursor.executemany("INSERT IGNORE INTO Match_Referee (match_id, referee_id) VALUES (%s, %s)", match_referee_buffer)
    if team_stadium_buffer:
        cursor.executemany("INSERT IGNORE INTO Team_stadium (team_id, stadium_id, round_id) VALUES (%s, %s, %s)", team_stadium_buffer)
        
    champ_id = fin_res[midF]['winner']
    cursor.execute("SELECT name FROM Team WHERE id=%s", (champ_id,))
    print(f"*** {year} CHAMPION: {cursor.fetchone()[0]} ***")

def generate_single_rr(team_ids):
    if len(team_ids) % 2 != 0: team_ids.append(None)
    n = len(team_ids)
    rounds = []
    ids = team_ids[:]
    for r in range(n-1):
        round_matches = []
        for i in range(n//2):
            t1, t2 = ids[i], ids[n-1-i]
            if t1 is not None and t2 is not None:
                if random.choice([True, False]): round_matches.append((t1, t2))
                else: round_matches.append((t2, t1))
        rounds.append(round_matches)
        ids.insert(1, ids.pop())
    return rounds

def setup_static_data(conn, cursor):
    print("Setting up static data...")
    # Teams
    teams = [(1000 + i, f"{fake.city()} BC") for i in range(NUM_TEAMS)]
    cursor.executemany("INSERT IGNORE INTO Team (id, name) VALUES (%s, %s)", teams)
    # Stadiums
    stadiums = [(fake.city(), f"{fake.company()} Arena", random.randint(10000, 90000)) for _ in range(NUM_STADIUMS)]
    cursor.executemany("INSERT IGNORE INTO Stadium (location, name, capacity) VALUES (%s, %s, %s)", stadiums)
    # Referees
    referees = [(3000 + i, fake.first_name(), fake.last_name()) for i in range(NUM_REFEREES)]
    cursor.executemany("INSERT IGNORE INTO Referee (id, first_name, last_name) VALUES (%s, %s, %s)", referees)
    # Events
    evts = ['Turnover', 'Steal', 'Block', 'Offensive Rebound', 'Defensive Rebound', 'Personal Foul', 'Technical Foul', 'Flagrant Foul', 'Offensive Foul', 'Substitution', 'Free Throw Made', 'Free Throw Attempt', '2-Point Field Goal Made', '2-Point Field Goal Attempt', '3-Point Field Goal Made', '3-Point Field Goal Attempt', 'Assist', 'Time running out']
    cursor.executemany("INSERT IGNORE INTO Event (id, name) VALUES (%s, %s)", [(i+1, n) for i, n in enumerate(evts)])
    # Persons
    pt_data = []
    p_data = []
    pid = 50000
    for tid in [t[0] for t in teams]:
        p_data.append((pid, fake.first_name(), fake.last_name(), 'Coach'))
        pt_data.append((pid, tid, datetime.now(), datetime.now(), 0))
        pid += 1
        for _ in range(PLAYERS_PER_TEAM):
            p_data.append((pid, fake.first_name_male(), fake.last_name(), 'Player'))
            pt_data.append((pid, tid, datetime.now(), datetime.now(), random.randint(0,99)))
            pid += 1
    cursor.executemany("INSERT IGNORE INTO Person (id, first_name, last_name, speciality) VALUES (%s, %s, %s, %s)", p_data)
    cursor.executemany("INSERT IGNORE INTO Person_Team (person_id, team_id, beginning, ending, shirt_num) VALUES (%s, %s, %s, %s, %s)", pt_data)

if __name__ == '__main__':
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            run_all_seasons(conn, cursor)
    finally:
        conn.close()