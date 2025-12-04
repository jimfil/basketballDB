import pymysql
import certifi
import os
from dotenv import load_dotenv

# 1. Load the variables from the .env file
load_dotenv()

# 2. Fetch variables (Best practice: use all caps for constants)
# If the variable isn't found, these will be None
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME   = os.getenv('DB_NAME')

def get_connection():
    con = pymysql.connect(
        host=DB_HOST, 
        user=DB_USER, 
        password=DB_PASS, 
        database=DB_NAME,
        port=4000,
        ssl={'ca': certifi.where()}
    )
    return con

def query(sql, params=()):
    returnable = []
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                returnable.append(dict(zip(cols, row)))
            return returnable               #epistrefei array pou se kathe thesi exei ena leksiko me key to id 
    

def get_persons(limit=0):
    sql = "SELECT id, first_name, last_name FROM person"
    params = []
    if limit != 0:
        sql += " LIMIT %s"
        params.append(limit)
    
    return query(sql, params)

def get_players(team_id, offset=0, limit=10):
    """Fetches players for a given team, paginated. Returns a list of dictionaries."""
    sql ='''SELECT p.speciality, p.id, p.first_name, p.last_name, pt.shirt_num, pt.team_id
            FROM person as p
            JOIN person_team as pt ON p.id = pt.person_id
            WHERE pt.team_id = %s
            LIMIT %s OFFSET %s'''
    params = (team_id, limit, offset * limit)
    return query(sql, params)

            

def get_teams(offset=0, limit=10):
    sql = "SELECT id, name FROM team"
    params = []
    if limit != 0:
        sql += " LIMIT %s OFFSET %s"
        params.extend([limit, offset * limit])
    
    return query(sql, params)
            
def get_matches():
    return query("SELECT * FROM `match`;")

def get_seasons():
    return query("SELECT * FROM season order by year desc;")

def get_matches_by_round(round_id):
    return query("SELECT id as match_id, home_team_id, away_team_id, match_date, status FROM `Match` WHERE round_id = %s;", (round_id,))

def get_match(match_id):
    return query("SELECT * FROM `Match` WHERE id = %s;", (match_id,))

def get_matches_by_team(team_id ,offset):
    return (query("SELECT name FROM Team WHERE id = %s;", (team_id,)), #onoma omadas
            query("""
                SELECT
                    m.id, m.match_date,
                    ht.name AS home_team_name,
                    at.name AS away_team_name
                FROM `Match` m
                JOIN `Team` ht ON m.home_team_id = ht.id
                JOIN `Team` at ON m.away_team_id = at.id
                WHERE m.home_team_id = %s OR m.away_team_id = %s
                ORDER BY m.match_date DESC
                LIMIT 10 OFFSET %s;
            """, (team_id, team_id, offset*10))) #agwnes

def get_referees_in_match(match_id):
    return query("SELECT r.* FROM match_referee JOIN referee r ON match_referee.referee_id = referee.id WHERE match_id = %s;", (match_id,))



def get_players_in_match(match_id):
    match = get_match(match_id)
    if not match:
        return []
    
    match = match[0]
    home_team_id = match['home_team_id']
    away_team_id = match['away_team_id']
    
    home_players = query("""
        SELECT p.* FROM Person p
        JOIN Person_Team pt ON p.id = pt.person_id
        WHERE pt.team_id = %s;
    """, (home_team_id,))
    
    away_players = query("""
        SELECT p.* FROM Person p
        JOIN Person_Team pt ON p.id = pt.person_id
        WHERE pt.team_id = %s;
    """, (away_team_id,))
    
    return home_players + away_players


def _execute_cud(sql, params=()):
    """
    A private helper function to execute Create, Update, or Delete statements.
    Returns True on success, False on any database error.
    """
    try:
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, params)
                con.commit()
                return True
    except pymysql.Error:
        # Catches IntegrityError (duplicates) and any other DB operational error.
        return False

def _execute_insert_and_get_id(sql, params=()):
    """
    A private helper for INSERT statements that need to return the new row's ID.
    Returns the new ID on success, None on failure.
    """
    try:
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, params)
                con.commit()
                return cur.lastrowid
    except pymysql.Error:
        return None

def create_season(year):
    return _execute_cud("INSERT INTO Season (year) VALUES (%s);", (year,))

def create_stadium(name, capacity):
    return _execute_cud("INSERT INTO Stadium (name, capacity) VALUES (%s, %s);", (name, capacity))

def create_person(first_name, last_name, speciality):
    return _execute_cud("INSERT INTO Person (first_name, last_name, speciality) VALUES (%s, %s, %s);", (first_name, last_name, speciality))

def create_referee(first_name, last_name):
    return _execute_cud("INSERT INTO referee (first_name, last_name) VALUES (%s, %s);", (first_name, last_name))

def create_event(name, type, subtype):
    return _execute_cud("INSERT INTO event (name, type, subtype) VALUES (%s, %s, %s);", (name, type, subtype))

def create_round(round_id, phase_id):
    return _execute_cud("INSERT INTO Round (round_id, phase_id) VALUES (%s, %s);", (round_id, phase_id))

def create_phase(year, phase_id):
    return _execute_insert_and_get_id("INSERT INTO phase (year, phase_id) VALUES (%s, %s);", (year, phase_id))

def create_team(name):
    return _execute_cud("INSERT INTO Team (NAME) VALUES (%s);", (name,))

def return_cud_tables(): #Return the tables for which you can create update and delete entries. 
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables = cur.fetchall()
            return [tables[0] for tables in tables]
        
def return_attributes(table_name): #Input is a santized dropdown box. Cannot use variable for some reason.
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute(f"SHOW COLUMNS FROM {table_name};")
            columns = cur.fetchall()
            return [col[0] for col in columns]
        
def read_table_entries_for_attribute(table_name,list_table_attribute = "*"):  #ean den baloume orisma epistrefei mono to id
    with get_connection() as con:
        with con.cursor() as cur:
            lista =[]
            for table_attribute in list_table_attribute:
                cur.execute(f"SELECT {table_attribute} FROM {table_name};")
                lista.append([entry[0] for entry in cur])
            return lista
            

def create_entry(table_name,list_user_input):
    col_names = return_attributes(table_name)
    columns_str = ", ".join(col_names) 
    placeholders = ", ".join(["%s"] * len(list_user_input)) #tha prepei na ta dinoume me thn swsth seira sto controller
    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    return _execute_cud(sql, list_user_input)

def delete_from_table(table_name,id):
    sql = f"DELETE FROM {table_name} WHERE id = %s;"
    return _execute_cud(sql, (id,))
        
def update_entry(table_name, entry_id, data_dict):
    """
    Securely updates one or more columns for an entry in a given table.

    :param table_name: The name of the table to update.
    :param entry_id: The ID of the row to update.
    :param data_dict: A dictionary where keys are column names and values are the new data.
    :return: True on success, False on failure.
    """
    if not data_dict:
        return False # Nothing to update

    set_clause = ", ".join([f"`{col}` = %s" for col in data_dict.keys()])
    sql = f"UPDATE `{table_name}` SET {set_clause} WHERE `id` = %s"
    
    values = list(data_dict.values()) + [entry_id]
    return _execute_cud(sql, tuple(values))

def update_player_shirt_number(player_id, new_shirt_number):
    """Updates a player's shirt number in the Person_Team table."""
    return _execute_cud("UPDATE Person_Team SET shirt_num = %s WHERE person_id = %s", (new_shirt_number, player_id))

def get_all_events():
    with get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT name FROM event")
                columns = cur.fetchall()
                event_names = [name[0] for name in columns]
                return event_names

def get_player_stats(player_id, offset=0, limit=10):
    """Fetches paginated stats for a given player. Returns a list of dictionaries."""
    sql ='''SELECT ec.match_id, e.name, ec.game_time
            FROM event_creation as ec
            JOIN event as e ON ec.event_id = e.id
            WHERE ec.person_id = %s
            LIMIT %s OFFSET %s'''
    params = (player_id, limit, offset * limit)
    return query(sql, params)


def get_match_stats(match_id, offset=0, limit=10):
    """Fetches paginated events for a given match. Returns a list of dictionaries."""
    sql = '''SELECT t.name as team_name, pt.shirt_num, p.last_name, e.name as event_name, ec.game_time
             FROM event_creation as ec
             JOIN event as e ON ec.event_id = e.id
             JOIN person as p ON ec.person_id = p.id
             JOIN person_team as pt ON p.id = pt.person_id
             JOIN team as t ON pt.team_id = t.id
             WHERE ec.match_id = %s
             ORDER BY ec.game_time, ec.event_id
             LIMIT %s OFFSET %s'''
    params = (match_id, limit, offset * limit)
    return query(sql, params)


def get_player_shot_stats(player_id, shot_type, match_id=None):
    with get_connection() as con:
        with con.cursor() as cur:
            sql = """
                SELECT e.name, COUNT(e.name)
                FROM event_creation AS ec
                JOIN event AS e ON ec.event_id = e.id
                WHERE ec.person_id = %s AND e.name IN (%s, %s)
            """
            params = [player_id, f"{shot_type} Made", f"{shot_type} Attempt"]

            if match_id:                            # An match_id = none einai gia ola ta matches
                sql += " AND ec.match_id = %s"
                params.append(match_id)

            sql += " GROUP BY e.name;"
            cur.execute(sql, tuple(params))
            return {k: int(v) for k, v in cur.fetchall()}

def calculate_group_stage_standings(phase_id):
    """
    Calculates group stage standings, correctly ranking teams within their dynamically identified groups.
    Qualification is based on being in the top 4 of a group.
    """
    sql = """
    WITH PhaseMatches AS (
        -- 1. Get all matches for the group stage phase
        SELECT m.id, m.home_team_id, m.away_team_id
        FROM `Match` m
        JOIN `Round` r ON m.round_id = r.id
        WHERE r.phase_id = %s AND m.status = 'Completed'
    ),
    TeamOpponents AS (
        -- 2. For each team, list all opponents they played against in this phase
        SELECT home_team_id AS team_id, away_team_id AS opponent_id FROM PhaseMatches
        UNION
        SELECT away_team_id AS team_id, home_team_id AS opponent_id FROM PhaseMatches
    ),
    TeamGroups AS (
        -- 3. Use a recursive CTE to find connected components (the groups).
        -- The group_identifier will be the smallest team ID in each connected component.
        WITH RECURSIVE GroupWalk (team_id, group_identifier) AS (
            SELECT id, id FROM Team WHERE id IN (SELECT team_id FROM TeamOpponents)
            UNION
            SELECT o.opponent_id, gw.group_identifier
            FROM GroupWalk gw JOIN TeamOpponents o ON gw.team_id = o.team_id
        )
        SELECT team_id, MIN(group_identifier) as group_identifier FROM GroupWalk GROUP BY team_id
    ),
    MatchScores AS (
        -- 4. Calculate scores for each match
        SELECT
            pm.id as match_id,
            pm.home_team_id,
            pm.away_team_id,
            SUM(CASE WHEN pt.team_id = pm.home_team_id AND e.name LIKE '%%Made' THEN
                CASE e.name WHEN '3-Point Field Goal Made' THEN 3 WHEN '2-Point Field Goal Made' THEN 2 ELSE 1 END
                ELSE 0 END) AS home_score,
            SUM(CASE WHEN pt.team_id = pm.away_team_id AND e.name LIKE '%%Made' THEN
                CASE e.name WHEN '3-Point Field Goal Made' THEN 3 WHEN '2-Point Field Goal Made' THEN 2 ELSE 1 END
                ELSE 0 END) AS away_score
        FROM PhaseMatches pm
        LEFT JOIN Event_Creation ec ON pm.id = ec.match_id
        LEFT JOIN Event e ON ec.event_id = e.id
        LEFT JOIN Person_Team pt ON ec.person_id = pt.person_id AND pt.team_id IN (pm.home_team_id, pm.away_team_id)
        GROUP BY pm.id, pm.home_team_id, pm.away_team_id
    ),
    Wins AS (
        -- 5. Count wins for each team
        SELECT
            CASE WHEN home_score > away_score THEN home_team_id ELSE away_team_id END as team_id,
            COUNT(*) as wins
        FROM MatchScores
        GROUP BY team_id
    ),
    RankedTeams AS (
        -- 6. Join all data and rank teams within their group
        SELECT
            t.name,
            tg.group_identifier,
            COALESCE(w.wins, 0) AS wins,
            (SELECT COUNT(*) FROM PhaseMatches pm WHERE pm.home_team_id = t.id OR pm.away_team_id = t.id) - COALESCE(w.wins, 0) AS losses,
            RANK() OVER (PARTITION BY tg.group_identifier ORDER BY COALESCE(w.wins, 0) DESC, t.id) as group_rank
        FROM Team t
        JOIN TeamGroups tg ON t.id = tg.team_id
        LEFT JOIN Wins w ON t.id = w.team_id
    )
    -- 7. Final selection and ordering
    SELECT name, wins, losses, group_identifier, group_rank
    FROM RankedTeams
    ORDER BY group_identifier, group_rank;
    """
    return query(sql, (phase_id,))

def calculate_standings_for_phase(phase_id):
    """Calculates standings for a non-group phase (e.g., knockouts)."""
    sql = """
        WITH MatchScores AS (
            SELECT
                m.id AS match_id,
                m.home_team_id,
                m.away_team_id,
                SUM(CASE WHEN pt.team_id = m.home_team_id AND e.name LIKE '%%Made' THEN
                    CASE e.name WHEN '3-Point Field Goal Made' THEN 3 WHEN '2-Point Field Goal Made' THEN 2 ELSE 1 END
                    ELSE 0 END) AS home_score,
                SUM(CASE WHEN pt.team_id = m.away_team_id AND e.name LIKE '%%Made' THEN
                    CASE e.name WHEN '3-Point Field Goal Made' THEN 3 WHEN '2-Point Field Goal Made' THEN 2 ELSE 1 END
                    ELSE 0 END) AS away_score
            FROM `Match` m
            JOIN `Round` r ON m.round_id = r.id
            LEFT JOIN Event_Creation ec ON m.id = ec.match_id
            LEFT JOIN Event e ON ec.event_id = e.id
            LEFT JOIN Person_Team pt ON ec.person_id = pt.person_id AND pt.team_id IN (m.home_team_id, m.away_team_id)
            WHERE r.phase_id = %s AND m.status = 'Completed'
            GROUP BY m.id, m.home_team_id, m.away_team_id
        ),
        Winners AS (
            SELECT
                CASE WHEN home_score > away_score THEN home_team_id ELSE away_team_id END as winner_id,
                CASE WHEN home_score < away_score THEN home_team_id ELSE away_team_id END as loser_id
            FROM MatchScores
        )
        SELECT
            t.id,
            t.name,
            COALESCE(w.wins, 0) AS wins,
            COALESCE(l.losses, 0) AS losses
        FROM Team t
        LEFT JOIN (SELECT winner_id, COUNT(*) as wins FROM Winners GROUP BY winner_id) w ON t.id = w.winner_id
        LEFT JOIN (SELECT loser_id, COUNT(*) as losses FROM Winners GROUP BY loser_id) l ON t.id = l.loser_id
        WHERE COALESCE(w.wins, 0) > 0 OR COALESCE(l.losses, 0) > 0
        ORDER BY wins DESC;
    """
    standings = query(sql, (phase_id,))
    # Convert Decimal to int for consistency
    for team_stats in standings:
        team_stats['wins'] = int(team_stats['wins'])
        team_stats['losses'] = int(team_stats['losses'])
    return standings        

def get_all_matches_with_names(offset=0, limit=10):
    """Fetches all matches, paginated, with team names, ordered by newest first."""
    sql = """
        WITH MatchScores AS (
            SELECT
                ec.match_id,
                SUM(CASE WHEN pt.team_id = m.home_team_id AND e.name LIKE '%%Made' THEN
                    CASE e.name WHEN '3-Point Field Goal Made' THEN 3 WHEN '2-Point Field Goal Made' THEN 2 ELSE 1 END
                    ELSE 0 END) AS home_score,
                SUM(CASE WHEN pt.team_id = m.away_team_id AND e.name LIKE '%%Made' THEN
                    CASE e.name WHEN '3-Point Field Goal Made' THEN 3 WHEN '2-Point Field Goal Made' THEN 2 ELSE 1 END
                    ELSE 0 END) AS away_score
            FROM Event_Creation ec
            JOIN `Match` m ON ec.match_id = m.id
            JOIN Event e ON ec.event_id = e.id
            JOIN Person_Team pt ON ec.person_id = pt.person_id AND pt.team_id IN (m.home_team_id, m.away_team_id)
            GROUP BY ec.match_id
        )
        SELECT
            m.id, m.match_date, m.status,
            ht.name AS home_team_name,
            at.name AS away_team_name,
            ms.home_score,
            ms.away_score
        FROM `Match` m
        JOIN `Team` ht ON m.home_team_id = ht.id
        JOIN `Team` at ON m.away_team_id = at.id
        LEFT JOIN MatchScores ms ON m.id = ms.match_id
        ORDER BY m.match_date DESC
        LIMIT %s OFFSET %s;
    """
    return query(sql, (limit, offset * limit))

def get_scores(match_id):
    """Calculates the final score for a given match."""
    sql = """
        SELECT
            m.home_team_id,
            m.away_team_id,
            SUM(CASE WHEN pt.team_id = m.home_team_id AND e.name LIKE '%%Made' THEN
                CASE e.name
                    WHEN '3-Point Field Goal Made' THEN 3
                    WHEN '2-Point Field Goal Made' THEN 2
                    ELSE 1
                END
            ELSE 0 END) AS home_score,
            SUM(CASE WHEN pt.team_id = m.away_team_id AND e.name LIKE '%%Made' THEN
                CASE e.name
                    WHEN '3-Point Field Goal Made' THEN 3
                    WHEN '2-Point Field Goal Made' THEN 2
                    ELSE 1
                END
            ELSE 0 END) AS away_score
        FROM `Match` m
        LEFT JOIN Event_Creation ec ON m.id = ec.match_id
        LEFT JOIN Event e ON ec.event_id = e.id
        LEFT JOIN Person_Team pt ON ec.person_id = pt.person_id AND pt.team_id IN (m.home_team_id, m.away_team_id)
        WHERE m.id = %s
        GROUP BY m.id, m.home_team_id, m.away_team_id;
    """
    result = query(sql, (match_id,))
    if not result:
        return None
    
    scores = result[0]
    return {
        scores['home_team_id']: int(scores['home_score']),
        scores['away_team_id']: int(scores['away_score'])
    }

def get_phases_by_season(year):
    return query("SELECT * FROM Phase WHERE year = %s ORDER BY id", (year,))

def get_phases(limit=0):
    sql = "SELECT id, name FROM phase"
    params = []
    if limit != 0:
        sql += " LIMIT %s"
        params.append(limit)
    
    return query(sql, params)

def get_matches_by_phase(phase_id):
    matches_sql = """
        SELECT m.id as match_id, m.home_team_id, m.away_team_id, m.match_date, m.status 
        FROM `Match` m
        JOIN `Round` r ON m.round_id = r.id
        WHERE r.phase_id = %s AND m.status = 'Completed'
    """
    matches = query(matches_sql, (phase_id,))
    return matches

def get_rounds(limit=0):
    sql = "SELECT id, name FROM round"
    params = []
    if limit != 0:
        sql += " LIMIT %s"
        params.append(limit)
    
    return query(sql, params)

def get_stadiums(limit=0):
    sql = "SELECT id, name FROM stadium"
    params = []
    if limit != 0:
        sql += " LIMIT %s"
        params.append(limit)
    
    return query(sql, params)

def get_rounds_by_phase(phase_id):
    return query("SELECT * FROM Round WHERE phase_id = %s ORDER BY id", (phase_id,))

def get_team_name(team_id):
    return query("SELECT name FROM Team WHERE id = %s", (team_id,))


def create_season(year):
    return _execute_cud("INSERT INTO Season (year) VALUES (%s);", (year,))


def get_person_attributes():
    return return_attributes('Person')


def create_player(player_data):
    try:
        with get_connection() as con:
            con.begin() # Start a transaction
            # Insert into Person table
            person_attributes = get_person_attributes()
            person_data = {key: player_data[key] for key in person_attributes if key in player_data}
            columns = ", ".join(person_data.keys())
            placeholders = ", ".join(["%s"] * len(person_data))
            sql_person = f"INSERT INTO Person ({columns}) VALUES ({placeholders})"
            with con.cursor() as cur:
                cur.execute(sql_person, list(person_data.values()))
                person_id = cur.lastrowid

            # Insert into Person_Team table
            team_id = player_data.get('team_id')
            shirt_num = player_data.get('shirt_num')
            if team_id and shirt_num:
                sql_person_team = "INSERT INTO Person_Team (person_id, team_id, shirt_num) VALUES (%s, %s, %s)"
                with con.cursor() as cur2:
                    cur2.execute(sql_person_team, (person_id, team_id, shirt_num))
            con.commit() # Commit the transaction
            return True
    except pymysql.Error:
        # If anything fails (person insert, team insert), the transaction is rolled back automatically by the `with` block exit.
        return False

def delete_player(player_id):
    """
    Deletes a player and all their related records within a transaction.
    The order of deletion is important to respect foreign key constraints.
    """
    try:
        with get_connection() as con:
            con.begin() # Start a transaction
            with con.cursor() as cur:
                # 1. Delete from child tables first (Event_Creation is handled by ON DELETE CASCADE)
                cur.execute("DELETE FROM Person_Team WHERE person_id = %s", (player_id,))
                # 2. Finally, delete from the parent table
                cur.execute("DELETE FROM Person WHERE id = %s", (player_id,))
            con.commit() # Commit all changes if successful
            return True
    except pymysql.Error:
        return False # The 'with' block will automatically roll back the transaction on error

def delete_team(team_id):
    """
    Deletes a team and its related records within a transaction.
    Prevents deletion if the team has participated in any matches.
    """
    try:
        with get_connection() as con:
            con.begin() # Start a transaction
            with con.cursor() as cur:
                # 1. Check if the team is part of any match. If so, we cannot delete it.
                cur.execute("SELECT 1 FROM `Match` WHERE home_team_id = %s OR away_team_id = %s LIMIT 1", (team_id, team_id))
                if cur.fetchone():
                    return False # Team has matches, deletion is not allowed.

                # 2. Delete from child tables first
                cur.execute("DELETE FROM Person_Team WHERE team_id = %s", (team_id,))
                cur.execute("DELETE FROM Team_stadium WHERE team_id = %s", (team_id,))
                
                # 3. Finally, delete from the parent table
                cur.execute("DELETE FROM Team WHERE id = %s", (team_id,))
            con.commit() # Commit all changes if successful
            return True
    except pymysql.Error:
        return False # The 'with' block will automatically roll back the transaction on error

def get_player_details(player_id):
    """Fetches detailed information for a single player."""
    sql = """
        SELECT p.first_name, p.last_name, pt.shirt_num
        FROM Person p
        LEFT JOIN Person_Team pt ON p.id = pt.person_id
        WHERE p.id = %s
    """
    result = query(sql, (player_id,))
    return result[0] if result else None


def create_match(match_data):
    """Inserts a new match into the Match table and returns its ID."""
    sql = """INSERT INTO `Match` (home_team_id, away_team_id, round_id, match_date, status)
             VALUES (%s, %s, %s, %s, %s)"""
    return _execute_insert_and_get_id(sql, (match_data['home_team_id'], match_data['away_team_id'], match_data['round_id'], match_data['match_date'], match_data['status']))
