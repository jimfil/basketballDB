import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

def get_db_connection():
    """Function to get a database connection."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=4000,
            ssl_ca=os.path.join(os.path.dirname(__file__), 'DigiCertGlobalRootCA.crt.pem')
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# For the Flask App
from flask import g

def get_db():
    """Function to get a database connection for flask app."""
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

def close_db(e=None):
    """Function to close a database connection for flask app."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Function to initialize the app with the database."""
    app.teardown_appcontext(close_db)
