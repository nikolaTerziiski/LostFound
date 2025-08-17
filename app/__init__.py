# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, mail
from . import models
from .models import User
from .api.routes import bp as api_bp
from .auth.routes import bp as auth_bp
from .listings.routes import listings_bp
from .errors import errors_bp
from .main.routes import bp as main_bp

def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)      
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))
    
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(errors_bp)
    return app
