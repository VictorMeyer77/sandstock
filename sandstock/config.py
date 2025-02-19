import os


class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://sql_admin:{{SQL_DB_ADMIN_PASSWORD}}@{{ENV}}-{{PROJECT}}-sql.postgres.database.azure.com:57000/"
        "{{ENV}}_erp?driver=ODBC+Driver+18+for+SQL+Server"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)
    LOGOUT_URL = "https://login.microsoftonline.com/{{TENANT_ID}}/oauth2/v2.0/logout"
    POST_LOGOUT_URL = "https://{{ENV}}-{{PROJECT}}.azurewebsites.net/logout"
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://sa:Te54%3Fko1@localhost:57000/master?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b"test_secret_key"
    WTF_CSRF_ENABLED = False
    DEBUG = False
