import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///stock.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)
    LOGOUT_URL = "https://login.microsoftonline.com/7b9f8ebb-f26f-463b-b786-27eb1e7b5d6a/oauth2/v2.0/logout"
    POST_LOGOUT_URL = "https://dev-sandstock.azurewebsites.net/logout"
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b"test_secret_key"
    WTF_CSRF_ENABLED = False
    DEBUG = False
