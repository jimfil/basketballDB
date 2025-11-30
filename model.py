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
    

def get_players(offset = 0): # dineis player id kai posa 10 thes na skipareis
    with get_connection() as con:
            with con.cursor() as cur:
                sql ='''SELECT p.speciality,p.id, p.first_name, p.last_name, pt.shirt_num,pt.team_id
                            FROM person as p
                            JOIN person_team as pt
                            ON p.id = pt.person_id
                            LIMIT 10 OFFSET %s'''
                cur.execute(sql,(offset*10))
                tuples = cur.fetchall()
                return tuples
            

def get_teams(offset = 0): # dineis player id kai posa 10 thes na skipareis
    with get_connection() as con:
            with con.cursor() as cur:
                sql ='''SELECT *
                            FROM team
                            LIMIT 10 OFFSET %s'''
                cur.execute(sql,(offset*10))
                tuples = cur.fetchall()
                return tuples
            
def get_matches():
    return query("SELECT * FROM `match`;")

def get_seasons():
    return query("SELECT * FROM Season;")

def get_phases_by_season(season_year):
    return query("SELECT * FROM Phase WHERE year = %s;", (season_year,))

def get_rounds_by_phase(phase_id):
    return query("SELECT * FROM Round WHERE phase_id = %s;", (phase_id,))

def get_matches_by_round(round_id):
    return query("SELECT * FROM `Match` WHERE matchday_id = %s;", (round_id,))

def get_match(match_id):
    return query("SELECT * FROM `Match` WHERE match_id = %s;", (match_id,))

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
        JOIN Person_Team pt ON p.person_id = pt.person_id
        WHERE pt.team_id = %s;
    """, (home_team_id,))
    
    away_players = query("""
        SELECT p.* FROM Person p
        JOIN Person_Team pt ON p.person_id = pt.person_id
        WHERE pt.team_id = %s;
    """, (away_team_id,))
    
    return home_players + away_players


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


def get_match_stats(id,i = 0): # 
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
                cur.execute(sql,(id,i*10))                
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
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("SELECT home_team_id, away_team_id FROM `match` WHERE id = %s", (match_id,))
            teams = cur.fetchone()
            if not teams:
                return None # Match not found
            team1_id, team2_id = teams
            sql_score = """
                SELECT
                    pt.team_id,
                    SUM(
                        CASE e.name
                            WHEN '3-Point Field Goal Made' THEN 3
                            WHEN '2-Point Field Goal Made' THEN 2
                            WHEN 'Free Throw Made' THEN 1
                            ELSE 0
                        END
                    ) AS total_score
                FROM event_creation AS ec
                JOIN event AS e 
                    ON ec.event_id = e.id
                JOIN person_team AS pt 
                    ON ec.person_id = pt.person_id
                WHERE ec.match_id = %s AND pt.team_id IN (%s, %s)
                GROUP BY pt.team_id;
            """
            cur.execute(sql_score, (match_id, team1_id, team2_id))
            results = dict(cur.fetchall())
            
            # Return a dictionary with team IDs and their scores, defaulting to 0.
            return {
                team1_id: int(results.get(team1_id, 0)),
                team2_id: int(results.get(team2_id, 0))
            }