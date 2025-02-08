import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///stock.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "victormeyer2ci@gmail.com"
    MAIL_PASSWORD = "lixp tvdp oqdj qhcp"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b"test_secret_key"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    DEBUG = False
