import os
from flask import Flask
from dotenv import load_dotenv # Import the loader

def create_app(test_config=None):
    # 1. Load environment variables from .env file
    load_dotenv()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        # Note: This currently sets up a local SQLite database. 
        # Since you have TiDB credentials in your .env, you will need to update 
        # your db.py file later to use those instead of this sqlite file.
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app