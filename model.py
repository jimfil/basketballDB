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

def return_cud_tables():
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables = cur.fetchall()
            return [tables[0] for tables in tables]
        
def return_attributes(table_name):
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute(f"SHOW COLUMNS FROM {table_name};")
            columns = cur.fetchall()
            return [col[0] for col in columns]
        
def read_table_entries_for_attribute(table_name,list_table_attribute):
    with get_connection() as con:
        with con.cursor() as cur:
            lista =[]
            for table_attribute in list_table_attribute:
                cur.execute(f"SELECT {table_attribute} FROM {table_name};")
                lista.append([entry[0] for entry in cur])
            return lista
            
        
print(read_table_entries_for_attribute("Team","name"))