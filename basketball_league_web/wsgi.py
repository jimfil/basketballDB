import sys
import os


project_home = '/home/andrupe/basketballDB'
app_dir = os.path.join(project_home, 'basketball_league_web')

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import create_app
from config import Config

# Create the Flask app instance for production
application = create_app(Config)
