import logging

from flask import Flask
from flask_migrate import Migrate

from sandstock.config import Config
from sandstock.extensions import db
from sandstock.routes import register_routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Register routes
    register_routes(app)

    # Logging Configuration
    if not app.debug:
        logging.basicConfig(level=logging.INFO)

    return app
