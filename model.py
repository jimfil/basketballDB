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
    

def get_teams():
    return query("SELECT * FROM Team;")

def get_players():
    return query("SELECT * FROM Person;")

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
        
def read_table_entries_for_attribute(table_name,list_table_attribute = ["id"]):  #ean den baloume orisma epistrefei mono to id
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
                cur.execute("SELECT * FROM event_creation WHERE person_id = %s LIMIT 10 OFFSET %s",(id,i*10))
                tuples = cur.fetchall()
                return tuples

def get_match_stats(id,i = 0): # 
    with get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM event_creation WHERE match_id = %s LIMIT 10 OFFSET %s",(id,i*10))
                tuples = cur.fetchall()
                return tuples