from app import create_app
from config import ProductionConfig # Or DevelopmentConfig for local development

app = create_app(ProductionConfig)