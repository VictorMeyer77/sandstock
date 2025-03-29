import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class Config:

    db_password = ""
    if os.getenv("TEST") != "true":
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url="https://{{ENV}}-sandstock-kv.vault.azure.net/", credential=credential)
        db_password = secret_client.get_secret("{{ENV}}-erp-db-password").value or ""

    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://{{ENV}}_erp_usr:"
        f"{db_password}"
        "@{{ENV}}-{{PROJECT}}-sql.database.windows.net:1433/"
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
