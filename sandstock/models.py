from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from sandstock.extensions import db


class User(db.Model, UserMixin):  # type: ignore
    __tablename__ = "dim_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow, nullable=False
    )
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Contact(db.Model):  # type: ignore
    __tablename__ = "dim_contact"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow, nullable=False
    )
    modified_by = db.Column(db.Integer, db.ForeignKey("dim_user.id"), nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Address(db.Model):  # type: ignore
    __tablename__ = "dim_address"

    id = db.Column(db.Integer, primary_key=True)
    street_address = db.Column(db.String(1000), nullable=False)
    city = db.Column(db.String(500), nullable=False)
    state = db.Column(db.String(500), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow, nullable=False
    )
    modified_by = db.Column(db.Integer, db.ForeignKey("dim_user.id"), nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Partner(db.Model):  # type: ignore
    __tablename__ = "dim_partner"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    contact_person = db.Column(db.String(200), nullable=True)
    address_id = db.Column(db.Integer, db.ForeignKey("dim_address.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("dim_contact.id"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow, nullable=False
    )
    modified_by = db.Column(db.Integer, db.ForeignKey("dim_user.id"), nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Warehouse(db.Model):  # type: ignore
    __tablename__ = "dim_warehouse"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey("dim_address.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("dim_contact.id"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow, nullable=False
    )
    modified_by = db.Column(db.Integer, db.ForeignKey("dim_user.id"), nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Product(db.Model):  # type: ignore
    __tablename__ = "dim_product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_label = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow, nullable=False
    )
    modified_by = db.Column(db.Integer, db.ForeignKey("dim_user.id"), nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Order(db.Model):  # type: ignore
    __tablename__ = "fact_order"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("dim_product.id"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey("dim_partner.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("dim_warehouse.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("dim_user.id"), nullable=False)
