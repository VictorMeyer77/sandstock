from flask import Flask
from flask_login import LoginManager

from sandstock.config import Config
from sandstock.models import db, User
from sandstock.routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        #db.drop_all()
        db.create_all()

    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
