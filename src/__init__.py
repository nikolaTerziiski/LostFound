import os

from flask import Flask, send_from_directory

from .admin.routes import admin_bp
from .api.routes import bp as api_bp
from .auth.routes import bp as auth_bp
from .config import Config, TestingConfig
from .errors import errors_bp
from .extensions import csrf, db, login_manager, mail, migrate
from .listings.routes import listings_bp
from .main.routes import bp as main_bp
from .models import User

config_by_name = {'development': Config, 'testing': TestingConfig}


def create_app(config_class: str = 'development') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_class])
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
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
    app.register_blueprint(admin_bp)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        upload_dir = os.path.join(app.root_path, '..',
                                  app.config['UPLOAD_PICTURES'])

        return send_from_directory(os.path.abspath(upload_dir), filename)

    return app
