from app import create_app
from config import DevelopmentConfig # Or ProductionConfig if you have it

app = create_app(DevelopmentConfig)