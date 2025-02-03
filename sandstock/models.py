import json
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "dim_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Contact(db.Model):
    __tablename__ = "dim_contact"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Address(db.Model):
    __tablename__ = "dim_address"

    id = db.Column(db.Integer, primary_key=True)
    street_address = db.Column(db.String(1000), nullable=False)
    city = db.Column(db.String(500), nullable=False)
    state = db.Column(db.String(500), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Partner(db.Model):
    __tablename__ = "dim_partner"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    contact_person = db.Column(db.String(200), nullable=True)
    address_id = db.Column(db.Integer, db.ForeignKey("dim_address.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("dim_contact.id"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Warehouse(db.Model):
    __tablename__ = "dim_warehouse"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey("dim_address.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("dim_contact.id"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Product(db.Model):
    __tablename__ = "dim_product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_label = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class Order(db.Model):
    __tablename__ = "fact_order"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("dim_product.id"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey("dim_partner.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("dim_warehouse.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)


# Change Data Capture


class ChangeLog(db.Model):
    __tablename__ = "change_log"

    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    operation = db.Column(db.String(10), nullable=False)  # INSERT, UPDATE, DELETE
    old_data = db.Column(db.Text, nullable=True)
    new_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def log_changes(mapper, connection, target, operation):
    old_data = {}
    new_data = {}

    if operation == "UPDATE":
        state = db.inspect(target)
        for attr in state.attrs:
            hist = state.get_history(attr.key, True)
            if hist.has_changes():
                old_data[attr.key] = hist.deleted[0]
                new_data[attr.key] = hist.added[0]

    elif operation == "INSERT":
        new_data = {c.name: getattr(target, c.name) for c in target.__table__.columns}

    elif operation == "DELETE":
        old_data = {c.name: getattr(target, c.name) for c in target.__table__.columns}

    change_log = ChangeLog(
        table_name=target.__tablename__,
        operation=operation,
        old_data=json.dumps(old_data, default=lambda x: x.isoformat(), indent=4) if old_data else None,
        new_data=json.dumps(new_data, default=lambda x: x.isoformat(), indent=4) if new_data else None,
    )
    db.session.add(change_log)


def add_listeners(model):
    event.listen(model, "after_insert", lambda m, c, t: log_changes(m, c, t, "INSERT"))
    event.listen(model, "after_update", lambda m, c, t: log_changes(m, c, t, "UPDATE"))
    event.listen(model, "after_delete", lambda m, c, t: log_changes(m, c, t, "DELETE"))


add_listeners(User)
add_listeners(Contact)
add_listeners(Address)
add_listeners(Partner)
add_listeners(Warehouse)
add_listeners(Product)
add_listeners(Order)
