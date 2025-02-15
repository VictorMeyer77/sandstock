import os


class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{os.getenv('ENV')}-{os.getenv('PROJECT')}-sql.postgres.database.azure.com:5432/{os.getenv('ENV')}_erp?user=psql_admin&password={os.getenv('SQL_DB_ADMIN_PASSWORD')}&sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)
    LOGOUT_URL = f"https://login.microsoftonline.com/{os.getenv('TENANT_ID')}/oauth2/v2.0/logout"
    POST_LOGOUT_URL = f"https://{os.getenv('ENV')}-{os.getenv('PROJECT')}.azurewebsites.net/logout"
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://test:test@localhost:5432/test_erp"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b"test_secret_key"
    WTF_CSRF_ENABLED = False
    DEBUG = False
