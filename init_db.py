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
conn = pymysql.connect(
    host=DB_HOST, 
    user=DB_USER, 
    password=DB_PASS, 
    port=4000,
    ssl={'ca': certifi.where()}
)
cursor = conn.cursor()
print(f"   (Resetting) Dropping '{DB_NAME}' if it exists...")
cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
print(f"2. Creating Database '{DB_NAME}'...")
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
conn.select_db(DB_NAME)

print("3. Reading matchDB.sql...")
try:
    with open('matchDB.sql', 'r') as f:
        # Split file by semicolons to get individual commands
        sql_commands = f.read().split(';')

    print(f"4. Executing {len(sql_commands)} commands...")
    for command in sql_commands:
        if command.strip(): # Skip empty lines
            try:
                cursor.execute(command)
            except Exception as e:
                # Print error but keep going (useful for debugging SQL syntax)
                print(f"  Warning on command: {e}")
    
    conn.commit()
    print("SUCCESS! Your schema has been loaded into TiDB.")

except FileNotFoundError:
    print("ERROR: Could not find matchDB.sql. Make sure it is in the same folder.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
finally:
    cursor.close()
    conn.close()