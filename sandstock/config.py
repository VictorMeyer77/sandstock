import os


class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://{{ENV}}-{{PROJECT}}-sql.postgres.database.azure.com:5432/"
        "{{ENV}}_erp?user=psql_admin&password={{SQL_DB_ADMIN_PASSWORD}}"
        "&sslmode=require"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)
    LOGOUT_URL = "https://login.microsoftonline.com/{{TENANT_ID}}/oauth2/v2.0/logout"
    POST_LOGOUT_URL = "https://{{ENV}}-{{PROJECT}}.azurewebsites.net/logout"
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://test:test@localhost:5432/test_erp"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b"test_secret_key"
    WTF_CSRF_ENABLED = False
    DEBUG = False
