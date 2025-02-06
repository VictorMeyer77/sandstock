from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

db = SQLAlchemy()
mail = Mail()
_serializer = None


def init_serializer(secret_key):
    global _serializer
    _serializer = URLSafeTimedSerializer(secret_key)

def get_serializer():
    if _serializer is None:
        raise RuntimeError("Serializer has not been initialized. Call init_serializer() in create_app().")
    return _serializer