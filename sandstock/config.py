import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///stock.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b"test_secret_key"
    WTF_CSRF_ENABLED = False
    DEBUG = False
