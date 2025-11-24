import pymysql
import certifi

# CONFIGURATION (Must match your settings.py)
DB_HOST = 'gateway01.eu-central-1.prod.aws.tidbcloud.com'      
DB_USER = '2HAKkCduYQbS5n9.root'  
DB_PASS = 'b9Iq1COyU4KdwnTc'   
DB_NAME = 'match_db' 


print("1. Connecting to TiDB Server...")
# Connect to the server generally (no specific DB yet)
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