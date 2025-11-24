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

def getConnection():
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
    with getConnection() as con:
        with con.cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                returnable.append(dict(zip(cols, row)))
            return returnable               #epistrefei array pou se kathe thesi exei ena leksiko me key to id 
    

def getTeams():
    return query("SELECT * FROM Team;")

def getPlayers():
    return query("SELECT * FROM Person;")

def createTeam(name):
    with getConnection() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO Team (NAME) VALUES (%s);",  (name))
            con.commit()
        except pymysql.err.IntegrityError as e:
            return  # IF e==pymysql.err.IntegrityError yparxei diplo onoma
