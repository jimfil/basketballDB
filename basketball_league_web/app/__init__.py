from flask import Flask
from config import Config
from . import db
from .extensions import login_manager, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    bcrypt.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        db_conn = db.get_db()
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data:
            return User(id=user_data['id'], username=user_data['username'], password_hash=user_data['password'])
        return None

    from .blueprints.auth import auth_bp
    from .blueprints.public import public_bp
    from .blueprints.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(current_user=current_user)

    return app
