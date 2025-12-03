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

def get_players(team,offset = 0): # dineis player id kai posa 10 thes na skipareis
    with get_connection() as con:
            with con.cursor() as cur:
                sql ='''SELECT p.speciality,p.id, p.first_name, p.last_name, pt.shirt_num,pt.team_id
                            FROM person as p
                            JOIN person_team as pt
                            ON p.id = pt.person_id
                            AND pt.team_id = %s
                            LIMIT 10 OFFSET %s'''
                cur.execute(sql,(team,offset*10))
                tuples = cur.fetchall()
                return tuples
            

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
            query("SELECT * FROM `Match` WHERE home_team_id = %s OR away_team_id = %s ORDER BY match_date DESC LIMIT 10 OFFSET %s;", (team_id, team_id, offset*10))) #agwnes

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


def create_season(year):
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO Season (year) VALUES (%s);",  (year,))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return  # IF e==pymysql.err.IntegrityError yparxei diplo onoma

def create_stadium(name, capacity):
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO Stadium (name, capacity) VALUES (%s, %s);",  (name, capacity))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return

def create_person(first_name, last_name, speciality):
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO Person (first_name, last_name, speciality) VALUES (%s, %s, %s);",  (first_name, last_name, speciality))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return

def create_referee(first_name, last_name):
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO referee (first_name, last_name) VALUES (%s, %s);",  (first_name, last_name))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return

def create_event(name, type, subtype):
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO event (name, type, subtype) VALUES (%s, %s, %s);",  (name, type, subtype))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return

def create_phase(year, name):
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO phase (year, name) VALUES (%s, %s);",  (year, name))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return

def create_team(name):
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO Team (NAME) VALUES (%s);",  (name))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return  # IF e==pymysql.err.IntegrityError yparxei diplo onoma

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
    with get_connection() as con:
        with con.cursor() as cur:
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            cur.execute(sql, list_user_input)
            con.commit()
            print("Entry created.")
            return

def delete_from_table(table_name,id):
    with get_connection() as con:
        with con.cursor() as cur:
            query = f"DELETE FROM {table_name} WHERE id = %s;"
            cur.execute(query, (id,))
            con.commit()
        
def update_entry(table_name, id, data_dict,gnwrisma):
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE {table_name} SET {gnwrisma}={data_dict} WHERE id= {id};")
            return

def get_all_events():
    with get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT name FROM event")
                columns = cur.fetchall()
                event_names = [name[0] for name in columns]
                return event_names

def get_player_stats(id,i = 0): # dineis player id kai posa 10 thes na skipareis
    with get_connection() as con:
            with con.cursor() as cur:
                sql ='''SELECT ec.match_id, e.name, ec.game_time
                            FROM event_creation as ec
                            JOIN event as e
                            ON ec.event_id = e.id
                            WHERE ec.person_id = %s
                            LIMIT 10 OFFSET %s'''
                cur.execute(sql,(id,i*10))
                tuples = cur.fetchall()
                return tuples


def get_match_stats(id,offset = 0): # 
    with get_connection() as con:
            with con.cursor() as cur:
                sql = '''SELECT pt.shirt_num, p.last_name, e.name, ec.game_time, t.name
                            FROM event_creation as ec
                            JOIN event as e
                            ON ec.event_id = e.id
                            JOIN person as p
                            ON ec.person_id = p.id
                            JOIN person_team as pt
                            ON p.id = pt.person_id
                            JOIN team as t
                            ON pt.team_id = t.id    
                            WHERE ec.match_id = %s
                            ORDER BY ec.game_time, ec.event_id
                            LIMIT 10 OFFSET %s'''
                cur.execute(sql,(id,offset*10))                
                tuples = cur.fetchall()
                return tuples

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
            cur.execute(sql, params)
            return dict(cur.fetchall())
        
def get_scores(match_id):
    sql = """
        SELECT 
            m.home_team_id,
            m.away_team_id,
            SUM(CASE WHEN pt.team_id = m.home_team_id AND e.name = '3-Point Field Goal Made' THEN 3 ELSE 0 END) +
            SUM(CASE WHEN pt.team_id = m.home_team_id AND e.name = '2-Point Field Goal Made' THEN 2 ELSE 0 END) +
            SUM(CASE WHEN pt.team_id = m.home_team_id AND e.name = 'Free Throw Made' THEN 1 ELSE 0 END) as home_score,
            SUM(CASE WHEN pt.team_id = m.away_team_id AND e.name = '3-Point Field Goal Made' THEN 3 ELSE 0 END) +
            SUM(CASE WHEN pt.team_id = m.away_team_id AND e.name = '2-Point Field Goal Made' THEN 2 ELSE 0 END) +
            SUM(CASE WHEN pt.team_id = m.away_team_id AND e.name = 'Free Throw Made' THEN 1 ELSE 0 END) as away_score
        FROM `Match` m
        LEFT JOIN Event_Creation ec ON m.id = ec.match_id
        LEFT JOIN Event e ON ec.event_id = e.id
        LEFT JOIN Person_Team pt ON ec.person_id = pt.person_id AND pt.team_id IN (m.home_team_id, m.away_team_id)
        WHERE m.id = %s
        GROUP BY m.home_team_id, m.away_team_id;
    """
    result = query(sql, (match_id,))
    
    if not result:
        # If the match doesn't exist, we can check for it to return an empty dict or None
        match_exists = query("SELECT id FROM `Match` WHERE id = %s", (match_id,))
        return {} if match_exists else None

    score_data = result[0]
    home_team_id = score_data['home_team_id']
    away_team_id = score_data['away_team_id']
    
    return {
        home_team_id: int(score_data.get('home_score') or 0),
        away_team_id: int(score_data.get('away_score') or 0)
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
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO Season (year) VALUES (%s);", (year,))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return  # Season already exists


def get_person_attributes():
    return return_attributes('Person')


def create_player(player_data):
    with get_connection() as con:
        cur = con.cursor()
        try:
            # Insert into Person table
            person_attributes = get_person_attributes()
            # We need to make sure we only try to insert the attributes that are in the table
            person_data = {key: player_data[key] for key in person_attributes if key in player_data}
            
            columns = ", ".join(person_data.keys())
            placeholders = ", ".join(["%s"] * len(person_data))
            
            sql = f"INSERT INTO Person ({columns}) VALUES ({placeholders})"
            cur.execute(sql, list(person_data.values()))
            
            # Get the id of the new player
            person_id = cur.lastrowid
            
            # Insert into Person_Team table
            team_id = player_data.get('team_id')
            shirt_num = player_data.get('shirt_num')
            
            if team_id and shirt_num:
                sql_person_team = "INSERT INTO Person_Team (person_id, team_id, shirt_num) VALUES (%s, %s, %s)"
                cur.execute(sql_person_team, (person_id, team_id, shirt_num))
            
            con.commit()
        except pymysql.err.IntegrityError as e:
            # Handle potential integrity errors, e.g., duplicate entries
            return {"error": str(e)}
