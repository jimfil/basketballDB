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
        port=4000,
        ssl={'ca': certifi.where()}
    )
    return conn

cur = getConnection.cursor()
cur.execute(f"use {DB_NAME};SELECT * FROM Team;")
for r in cur:
    print(r)
cur.close()
