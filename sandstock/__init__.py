import logging

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from sandstock.config import Config
from sandstock.extensions import db, init_serializer, mail
from sandstock.models import User
from sandstock.routes import register_routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    mail.init_app(app)
    init_serializer(app.config["SECRET_KEY"])

    # Setup Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register routes
    register_routes(app)

    # Logging Configuration
    if not app.debug:
        logging.basicConfig(level=logging.INFO)

    return app
