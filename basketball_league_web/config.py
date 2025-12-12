import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'your_user')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'your_password')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'basketball_db')

class DevelopmentConfig(Config):
    DEBUG = True
