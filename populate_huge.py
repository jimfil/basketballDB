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
# The tournament requires exactly 32 teams for the main draw
NUM_TEAMS = 32 
NUM_STADIUMS = 32
NUM_REFEREES = 50
PLAYERS_PER_TEAM = 12 
START_YEAR = 2024

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
    Returns a dictionary: {match_id: {'winner': team_id, 'loser': team_id, 'score': (h_pts, a_pts)}}
    """
    results = {}
    event_buffer = []
    
    # Pre-fetch stadium/referee checks if needed, but we focus on events here.
    
    for match_info in matches_data:
        m_id, home_id, away_id, m_date = match_info
        
        # Determine Game Start Time
        if isinstance(m_date, str):
            base_date = datetime.strptime(m_date, '%Y-%m-%d')
        else:
            base_date = datetime.combine(m_date, datetime.min.time())
            
        # Rosters
        if home_id not in team_rosters or away_id not in team_rosters:
            print(f"Skipping match {m_id} due to missing roster.")
            continue
            
        home_roster = team_rosters[home_id][:]
        away_roster = team_rosters[away_id][:]
        
        # On Court / Bench
        on_court = { 'home': set(home_roster[:5]), 'away': set(away_roster[:5]) }
        bench = { 'home': list(home_roster[5:]), 'away': list(away_roster[5:]) }
        
        # Stats
        scores = {'home': 0, 'away': 0}
        player_fouls = {pid: 0 for pid in home_roster + away_roster}
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
                # Time usage
                time_used = random.randint(8, 24)
                current_time += timedelta(seconds=time_used)
                if current_time >= end_time: break

                atk = possession
                dfn = 'away' if atk == 'home' else 'home'
                
                attacker = random.choice(list(on_court[atk]))
                defender = random.choice(list(on_court[dfn]))
                
                outcome = random.random()
                
                # 1. Turnover (15%)
                if outcome < 0.15:
                    etype = random.choice(['Turnover', 'Steal', 'Time running out'])
                    if etype == 'Steal':
                        log(defender, 'Steal', current_time)
                        log(attacker, 'Turnover', current_time)
                    else:
                        log(attacker, etype, current_time)
                    possession = dfn # Switch
                
                # 2. Foul (15%)
                elif outcome < 0.30:
                    ftype = random.choices(['Personal Foul', 'Offensive Foul', 'Technical Foul', 'Flagrant Foul'], weights=[70,15,10,5])[0]
                    
                    if ftype == 'Offensive Foul':
                        log(attacker, ftype, current_time)
                        player_fouls[attacker] += 1
                        team_fouls[atk] += 1
                        possession = dfn
                        # Disqualification Check
                        if player_fouls[attacker] >= 5 and bench[atk]:
                            sub = bench[atk].pop(0)
                            on_court[atk].remove(attacker)
                            on_court[atk].add(sub)
                            log(attacker, 'Substitution', current_time)
                            log(sub, 'Substitution', current_time)
                    else:
                        log(defender, ftype, current_time)
                        player_fouls[defender] += 1
                        if ftype != 'Technical Foul': team_fouls[dfn] += 1
                        
                        shots = 0
                        if ftype == 'Flagrant Foul': shots = 2
                        elif ftype == 'Technical Foul': shots = 1
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
                            possession = atk # Side out
                            
                        # Disqualification Check
                        if player_fouls[defender] >= 5 and bench[dfn]:
                            sub = bench[dfn].pop(0)
                            on_court[dfn].remove(defender)
                            on_court[dfn].add(sub)
                            log(defender, 'Substitution', current_time)
                            log(sub, 'Substitution', current_time)

                # 3. Shot (70%)
                else:
                    is_3pt = random.random() < 0.35
                    s_type = '3-Point Field Goal' if is_3pt else '2-Point Field Goal'
                    pts = 3 if is_3pt else 2
                    is_made = random.choice([True, False])
                    
                    if is_made:
                        # Assist Rule: Must happen before shot
                        teammate = random.choice(list(on_court[atk] - {attacker}))
                        log(teammate, 'Assist', current_time)
                        
                        log(attacker, f"{s_type} Made", current_time)
                        scores[atk] += pts
                        
                        # And-1 Check
                        if random.random() < 0.05:
                            log(defender, 'Personal Foul', current_time)
                            log(attacker, 'Free Throw Made', current_time)
                            scores[atk] += 1
                        
                        possession = dfn
                    else:
                        log(attacker, f"{s_type} Attempt", current_time)
                        # Rebound
                        if random.random() < 0.1: # Block
                            log(defender, 'Block', current_time)
                            log(random.choice(list(on_court[dfn])), 'Defensive Rebound', current_time)
                            possession = dfn
                        elif random.random() < 0.75:
                            log(random.choice(list(on_court[dfn])), 'Defensive Rebound', current_time)
                            possession = dfn
                        else:
                            log(random.choice(list(on_court[atk])), 'Offensive Rebound', current_time)
                            possession = atk # Keep

                # Substitutions (Random)
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

        # Overtime if tied
        while scores['home'] == scores['away']:
            # Simple coin flip score adder for simplicity in simulation to break ties
            scores[random.choice(['home', 'away'])] += 2
        
        winner = home_id if scores['home'] > scores['away'] else away_id
        loser = away_id if winner == home_id else home_id
        
        results[m_id] = {'winner': winner, 'loser': loser, 'score': scores}
    
    # Bulk Insert Events
    if event_buffer:
        cursor.executemany("INSERT INTO Event_Creation (match_id, person_id, event_id, game_time) VALUES (%s, %s, %s, %s)", event_buffer)
    
    return results

# --- TOURNAMENT MANAGER ---

def run_tournament(conn, cursor):
    print("--- STARTING TOURNAMENT GENERATION (BCL FORMAT) ---")
    
    # 0. Setup Static Data
    setup_static_data(conn, cursor)
    conn.commit()
    
    # Fetch Data
    cursor.execute("SELECT id FROM Team")
    all_teams = [r[0] for r in cursor.fetchall()]
    if len(all_teams) < 32:
        print("Error: Need at least 32 teams.")
        return
    teams_32 = all_teams[:32] # Main Draw
    
    cursor.execute("SELECT team_id, person_id FROM Person_Team")
    rosters = {}
    for t, p in cursor.fetchall():
        if t not in rosters: rosters[t] = []
        rosters[t].append(p)
        
    cursor.execute("SELECT name, id FROM Event")
    e_map = {r[0]: r[1] for r in cursor.fetchall()}
    
    cursor.execute("SELECT id FROM Stadium")
    stadiums = [r[0] for r in cursor.fetchall()]
    
    match_id_counter = 70000
    
    # --- ROUND 1: REGULAR SEASON (Groups) ---
    print("\n[ROUND 1] Group Stage (8 Groups of 4)")
    # Shuffle and Split
    random.shuffle(teams_32)
    groups = [teams_32[i:i+4] for i in range(0, 32, 4)] # 8 groups
    
    r1_standings = {t: {'wins': 0, 'points': 0} for t in teams_32}
    r1_matches = []
    
    start_date = date(START_YEAR, 10, 1)
    
    for g_idx, group in enumerate(groups):
        # Double Round Robin
        schedule = generate_double_rr(group)
        for day, h, a in schedule:
            mid = match_id_counter
            match_id_counter += 1
            mdate = start_date + timedelta(days=(day-1)*7)
            # Store match data for simulation
            r1_matches.append((mid, h, a, mdate))
            # DB Insert
            cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 1, %s, %s, %s)", (mid, mdate, random.choice(stadiums), h, a))

    conn.commit()
    
    # Simulate Round 1
    print(f"   -> Simulating {len(r1_matches)} matches...")
    results = simulate_match_batch(cursor, r1_matches, rosters, e_map)
    conn.commit()
    
    # Process Standings
    for res in results.values():
        w = res['winner']
        r1_standings[w]['wins'] += 1
    
    # Determine Qualifiers
    round_3_qualifiers = [] # 1st place
    round_2_teams = []      # 2nd & 3rd place
    
    for group in groups:
        # Sort by wins
        sorted_g = sorted(group, key=lambda t: r1_standings[t]['wins'], reverse=True)
        round_3_qualifiers.append(sorted_g[0]) # 1st -> Round 3 directly
        round_2_teams.append((sorted_g[1], sorted_g[2])) # 2nd vs 3rd -> Round 2
        
    # --- ROUND 2: PLAY-INS (Best of 3) ---
    print("\n[ROUND 2] Play-Ins (Best of 3)")
    r2_winners = []
    r2_matches = []
    r2_date = start_date + timedelta(days=70) # Jan
    
    for pair in round_2_teams:
        team_high, team_low = pair # 2nd (High) vs 3rd (Low)
        # H-A-H format
        wins = {team_high: 0, team_low: 0}
        
        # Game 1 (High Home)
        mid = match_id_counter; match_id_counter += 1
        r2_matches.append((mid, team_high, team_low, r2_date))
        cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 2, %s, %s, %s)", (mid, r2_date, random.choice(stadiums), team_high, team_low))
        
        # Game 2 (Low Home)
        mid2 = match_id_counter; match_id_counter += 1
        r2_matches.append((mid2, team_low, team_high, r2_date + timedelta(days=3)))
        cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 2, %s, %s, %s)", (mid2, r2_date + timedelta(days=3), random.choice(stadiums), team_low, team_high))
        
        # Simulate G1 & G2 immediately to check for G3
        conn.commit()
        batch_res = simulate_match_batch(cursor, r2_matches[-2:], rosters, e_map)
        conn.commit()
        
        for m in batch_res: wins[batch_res[m]['winner']] += 1
        
        winner = None
        if wins[team_high] == 2: winner = team_high
        elif wins[team_low] == 2: winner = team_low
        else:
            # Game 3 (High Home)
            mid3 = match_id_counter; match_id_counter += 1
            g3_data = [(mid3, team_high, team_low, r2_date + timedelta(days=6))]
            cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 2, %s, %s, %s)", (mid3, r2_date + timedelta(days=6), random.choice(stadiums), team_high, team_low))
            conn.commit()
            
            res3 = simulate_match_batch(cursor, g3_data, rosters, e_map)
            winner = res3[mid3]['winner']
            conn.commit()
            
        r2_winners.append(winner)

    # --- ROUND 3: ROUND OF 16 (4 Groups of 4) ---
    print("\n[ROUND 3] Round of 16")
    r16_teams = round_3_qualifiers + r2_winners
    random.shuffle(r16_teams)
    r16_groups = [r16_teams[i:i+4] for i in range(0, 16, 4)]
    
    r3_standings = {t: 0 for t in r16_teams}
    r3_matches = []
    r3_date = r2_date + timedelta(days=20)
    
    for group in r16_groups:
        schedule = generate_double_rr(group)
        for day, h, a in schedule:
            mid = match_id_counter; match_id_counter += 1
            md = r3_date + timedelta(days=(day-1)*7)
            r3_matches.append((mid, h, a, md))
            cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 3, %s, %s, %s)", (mid, md, random.choice(stadiums), h, a))
            
    conn.commit()
    res_r3 = simulate_match_batch(cursor, r3_matches, rosters, e_map)
    conn.commit()
    
    for r in res_r3.values(): r3_standings[r['winner']] += 1
    
    qf_qualifiers = []
    for g in r16_groups:
        s_g = sorted(g, key=lambda t: r3_standings[t], reverse=True)
        qf_qualifiers.extend(s_g[:2]) # Top 2 advance
        
    # --- ROUND 4: QUARTER FINALS (Best of 3) ---
    print("\n[ROUND 4] Quarter-Finals")
    # 8 teams -> 4 pairs
    random.shuffle(qf_qualifiers)
    pairs = [(qf_qualifiers[i], qf_qualifiers[i+1]) for i in range(0, 8, 2)]
    
    ff_teams = []
    r4_date = r3_date + timedelta(days=60)
    
    for t1, t2 in pairs:
        # Simplified Best of 3 sim (Just checking winner logic)
        wins = {t1: 0, t2: 0}
        series_matches = []
        
        # G1
        mid1 = match_id_counter; match_id_counter += 1
        series_matches.append((mid1, t1, t2, r4_date))
        cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 4, %s, %s, %s)", (mid1, r4_date, random.choice(stadiums), t1, t2))
        
        # G2
        mid2 = match_id_counter; match_id_counter += 1
        series_matches.append((mid2, t2, t1, r4_date + timedelta(days=3)))
        cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 4, %s, %s, %s)", (mid2, r4_date + timedelta(days=3), random.choice(stadiums), t2, t1))
        
        conn.commit()
        s_res = simulate_match_batch(cursor, series_matches, rosters, e_map)
        conn.commit()
        
        for m in s_res: wins[s_res[m]['winner']] += 1
        
        if wins[t1] == 2: ff_teams.append(t1)
        elif wins[t2] == 2: ff_teams.append(t2)
        else:
            # G3
            mid3 = match_id_counter; match_id_counter += 1
            g3 = [(mid3, t1, t2, r4_date + timedelta(days=6))]
            cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 4, %s, %s, %s)", (mid3, r4_date + timedelta(days=6), random.choice(stadiums), t1, t2))
            conn.commit()
            r3 = simulate_match_batch(cursor, g3, rosters, e_map)
            conn.commit()
            ff_teams.append(r3[mid3]['winner'])
            
    # --- ROUND 5: FINAL FOUR ---
    print("\n[ROUND 5] Final Four")
    ff_date = r4_date + timedelta(days=30)
    
    # Semis
    s1_home, s1_away = ff_teams[0], ff_teams[1]
    s2_home, s2_away = ff_teams[2], ff_teams[3]
    
    semi_matches = []
    mid_s1 = match_id_counter; match_id_counter += 1
    mid_s2 = match_id_counter; match_id_counter += 1
    
    semi_matches.append((mid_s1, s1_home, s1_away, ff_date))
    semi_matches.append((mid_s2, s2_home, s2_away, ff_date))
    
    cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 5, %s, %s, %s)", (mid_s1, ff_date, random.choice(stadiums), s1_home, s1_away))
    cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 5, %s, %s, %s)", (mid_s2, ff_date, random.choice(stadiums), s2_home, s2_away))
    
    conn.commit()
    semi_res = simulate_match_batch(cursor, semi_matches, rosters, e_map)
    conn.commit()
    
    finalists = [semi_res[mid_s1]['winner'], semi_res[mid_s2]['winner']]
    
    # FINAL
    print("\n[THE FINAL]")
    mid_f = match_id_counter
    cursor.execute("INSERT INTO `Match` (id, match_date, status, matchday_id, stadium_id, home_team_id, away_team_id) VALUES (%s, %s, 'Completed', 5, %s, %s, %s)", (mid_f, ff_date + timedelta(days=2), random.choice(stadiums), finalists[0], finalists[1]))
    conn.commit()
    
    fin_res = simulate_match_batch(cursor, [(mid_f, finalists[0], finalists[1], ff_date+timedelta(days=2))], rosters, e_map)
    conn.commit()
    
    champion = fin_res[mid_f]['winner']
    cursor.execute("SELECT name FROM Team WHERE id=%s", (champion,))
    print(f"*** TOURNAMENT CHAMPION: {cursor.fetchone()[0]} ***")

def generate_double_rr(team_ids):
    # Standard algorithm
    if len(team_ids) % 2 != 0: team_ids.append(None)
    n = len(team_ids)
    matches = []
    for r in range(n-1):
        for i in range(n//2):
            t1, t2 = team_ids[i], team_ids[n-1-i]
            if t1 and t2: matches.append((r+1, t1, t2))
        team_ids.insert(1, team_ids.pop())
    
    # Double it
    doubled = matches[:]
    for d, h, a in matches:
        doubled.append((d+n-1, a, h))
    return doubled

def setup_static_data(conn, cursor):
    print("Setting up static data...")
    # Seasons
    cursor.execute("INSERT IGNORE INTO Season (year) VALUES (%s)", (START_YEAR,))
    # Teams
    teams = [(1000 + i, f"{fake.city()} BC") for i in range(NUM_TEAMS)]
    cursor.executemany("INSERT IGNORE INTO Team (id, name) VALUES (%s, %s)", teams)
    # Stadiums
    stadiums = [(fake.city(), f"{fake.company()} Arena", random.randint(10000, 90000)) for _ in range(NUM_STADIUMS)]
    cursor.executemany("INSERT IGNORE INTO Stadium (location, name, capacity) VALUES (%s, %s, %s)", stadiums)
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
            run_tournament(conn, cursor)
    finally:
        conn.close()