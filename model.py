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
    conn = pymysql.connect(
        host=DB_HOST, 
        user=DB_USER, 
        password=DB_PASS, 
        database=DB_NAME,
        port=4000,
        ssl={'ca': certifi.where()}
    )
    return conn

def query(sql, params=()):
    with getConnection() as con:
        cur = con.execute(sql, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    
lista = query("SELECT * FROM Team;")
for r in lista:
    print(r)

