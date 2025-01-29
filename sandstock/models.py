from email.policy import default

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Metadata

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    #deleted = db.Column(db.Boolean, nullable=False, default=False)
    #created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Business

class Category(db.Model):
    __tablename__ = "dim_category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


class Supplier(db.Model):
    __tablename__ = "dim_supplier"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    # todo full address
    #contact_person = db.Column(db.String(200), nullable=True)
    #email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    #deleted = db.Column(db.Boolean, nullable=False, default=False)
    #created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Product(db.Model):
    __tablename__ = "dim_product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("dim_category.id"), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("dim_supplier.id"), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    category = db.relationship("Category", backref=db.backref("products", lazy=True))
    supplier = db.relationship("Supplier", backref=db.backref("products", lazy=True))


class Transaction(db.Model):
    __tablename__ = "fact_transaction"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("dim_product.id"), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # "IN" or "OUT"
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    product = db.relationship("Product", backref=db.backref("transactions", lazy=True))
