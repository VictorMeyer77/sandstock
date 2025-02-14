from urllib.parse import urlencode

import pytest

from sandstock import create_app, db
from sandstock.config import TestingConfig
from sandstock.models import Address, Contact, Order, Partner, Product, Warehouse


@pytest.fixture
def app():
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def test_logout(client):
    headers = {"X-MS-CLIENT-PRINCIPAL-ID": "test-client-id"}
    response = client.get("/logout", headers=headers)
    assert response.status_code == 302
    params = {
        "post_logout_redirect_uri": TestingConfig.POST_LOGOUT_URL,
        "client_id": "test-client-id",
    }
    expected_url = f"{TestingConfig.LOGOUT_URL}?{urlencode(params)}"
    assert response.headers["Location"] == expected_url


def test_home(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Partners" in response.data
    assert b"Warehouses" in response.data
    assert b"Products" in response.data
    assert b"Orders" in response.data


def test_add_partner(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    response = client.post(
        "/partner/add",
        data={
            "name": "Test Partner",
            "contact_person": "John Doe",
            "email": "contact@testpartner.com",
            "phone_number": "123456789",
            "street_address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA",
        },
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )

    assert b"Partner added successfully!" in response.data
    partner = Partner.query.filter_by(name="Test Partner").first()
    assert partner is not None
    assert partner.contact_person == "John Doe"
    assert partner.modified_by == "user@mail.com"
    address = Address.query.filter_by(id=partner.address_id).first()
    assert address is not None
    assert address.city == "New York"
    contact = Contact.query.filter_by(id=partner.contact_id).first()
    assert contact is not None
    assert contact.email == "contact@testpartner.com"


# Partner


def test_edit_partner(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testpartner.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    partner = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    db.session.add(partner)
    db.session.commit()

    response = client.get(f"/partner/{partner.id}/edit")
    assert response.status_code == 200

    response = client.post(
        f"/partner/{partner.id}/edit",
        data={
            "name": "Updated Partner Name",
            "contact_person": "Jane Doe",
            "email": "updated@testpartner.com",
            "phone_number": "987654321",
            "street_address": "456 Elm Street",
            "city": "Los Angeles",
            "state": "CA",
            "postal_code": "90001",
            "country": "USA",
        },
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )

    assert b"Partner updated successfully!" in response.data

    updated_partner = db.session.get(Partner, partner.id)
    assert updated_partner.name == "Updated Partner Name"
    assert updated_partner.contact_person == "Jane Doe"
    assert updated_partner.modified_by == "user@mail.com"
    updated_contact = db.session.get(Contact, updated_partner.contact_id)
    assert updated_contact.email == "updated@testpartner.com"
    updated_address = db.session.get(Address, updated_partner.address_id)
    assert updated_address.city == "Los Angeles"


def test_delete_partner(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(email="contact@testpartner.com", phone_number="123456789", modified_by="test@gmail.com")
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    partner = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    db.session.add(partner)
    db.session.commit()

    response = client.post(
        f"/partner/{partner.id}/delete", headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"}, follow_redirects=True
    )
    assert b"Partner deleted successfully!" in response.data
    deleted_partner = db.session.get(Partner, partner.id)
    assert deleted_partner.modified_by == "user@mail.com"
    deleted_partner = db.session.get(Partner, partner.id)
    assert deleted_partner.deleted is True


def test_get_partners(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(email="contact@testpartner.com", phone_number="123456789", modified_by="test@gmail.com")
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    partner_a = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    partner_b = Partner(
        name="Test Other",
        contact_person="Jane Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    partner_c = Partner(
        name="Test Other",
        contact_person="Jane Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
        deleted=True,
    )
    db.session.add(partner_a)
    db.session.add(partner_b)
    db.session.add(partner_c)
    db.session.commit()

    response = client.get("/partner/get?query=", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 2
    assert data[0]["name"] == "Test Partner"
    assert data[1]["name"] == "Test Other"

    for partner in data:
        assert not partner["deleted"]


def test_get_partners_with_filter(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(email="contact@testpartner.com", phone_number="123456789", modified_by="test@gmail.com")
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    partner_a = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    partner_b = Partner(
        name="Test Other",
        contact_person="Jane Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    partner_c = Partner(
        name="Test Other",
        contact_person="Jane Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
        deleted=True,
    )
    db.session.add(partner_a)
    db.session.add(partner_b)
    db.session.add(partner_c)
    db.session.commit()

    response = client.get("/partner/get?query=Other", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Other"


# Warehouse


def test_add_warehouse(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    response = client.post(
        "/warehouse/add",
        data={
            "name": "Test Warehouse",
            "email": "contact@testwarehouse.com",
            "phone_number": "123456789",
            "street_address": "123 Warehouse Street",
            "city": "Warehouse City",
            "state": "WS",
            "postal_code": "10002",
            "country": "Warehouse Country",
        },
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )

    assert b"Warehouse added successfully!" in response.data

    warehouse = Warehouse.query.filter_by(name="Test Warehouse").first()
    assert warehouse is not None
    assert warehouse.name == "Test Warehouse"
    assert warehouse.modified_by == "user@mail.com"
    contact = Contact.query.filter_by(id=warehouse.contact_id).first()
    assert contact is not None
    assert contact.email == "contact@testwarehouse.com"
    address = Address.query.filter_by(id=warehouse.address_id).first()
    assert address is not None
    assert address.city == "Warehouse City"


def test_edit_warehouse(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testwarehouse.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Warehouse Street",
        city="Warehouse City",
        state="WS",
        postal_code="10002",
        country="Warehouse Country",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    warehouse = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    db.session.add(warehouse)
    db.session.commit()

    response = client.get(f"/warehouse/{warehouse.id}/edit")
    assert response.status_code == 200

    response = client.post(
        f"/warehouse/{warehouse.id}/edit",
        data={
            "name": "Updated Warehouse Name",
            "email": "updated@testwarehouse.com",
            "phone_number": "987654321",
            "street_address": "456 New Street",
            "city": "New City",
            "state": "NC",
            "postal_code": "20002",
            "country": "New Country",
        },
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )

    assert b"Warehouse updated successfully!" in response.data

    updated_warehouse = db.session.get(Warehouse, warehouse.id)
    assert updated_warehouse.name == "Updated Warehouse Name"
    assert updated_warehouse.modified_by == "user@mail.com"
    updated_contact = db.session.get(Contact, updated_warehouse.contact_id)
    assert updated_contact.email == "updated@testwarehouse.com"
    updated_address = db.session.get(Address, updated_warehouse.address_id)
    assert updated_address.city == "New City"


def test_delete_warehouse(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testwarehouse.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Warehouse Street",
        city="Warehouse City",
        state="WS",
        postal_code="10002",
        country="Warehouse Country",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    warehouse = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    db.session.add(warehouse)
    db.session.commit()

    response = client.post(
        f"/warehouse/{warehouse.id}/delete",
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )
    assert b"Warehouse deleted successfully!" in response.data
    deleted_warehouse = db.session.get(Warehouse, warehouse.id)
    assert deleted_warehouse.deleted is True
    assert deleted_warehouse.modified_by == "user@mail.com"


def test_get_warehouses(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testwarehouse.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Warehouse Street",
        city="Warehouse City",
        state="WS",
        postal_code="10002",
        country="Warehouse Country",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    warehouse_a = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse_b = Warehouse(
        name="Test Other Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse_c = Warehouse(
        name="Deleted Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
        deleted=True,
    )
    db.session.add(warehouse_a)
    db.session.add(warehouse_b)
    db.session.add(warehouse_c)
    db.session.commit()

    response = client.get("/warehouse/get?query=", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Warehouse"
    assert data[1]["name"] == "Test Other Warehouse"
    for warehouse in data:
        assert not warehouse["deleted"]


def test_get_warehouses_with_filter(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testwarehouse.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Warehouse Street",
        city="Warehouse City",
        state="WS",
        postal_code="10002",
        country="Warehouse Country",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    warehouse_a = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse_b = Warehouse(
        name="Test Other Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse_c = Warehouse(
        name="Deleted Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
        deleted=True,
    )
    db.session.add(warehouse_a)
    db.session.add(warehouse_b)
    db.session.add(warehouse_c)
    db.session.commit()

    response = client.get("/warehouse/get?query=Other", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Other Warehouse"


# Product


def test_add_product(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    response = client.post(
        "/product/add",
        data={"name": "Test Product", "category_label": "Test Category", "description": "This is a test product."},
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )

    assert b"Product added successfully!" in response.data

    product = Product.query.filter_by(name="Test Product").first()
    assert product is not None
    assert product.name == "Test Product"
    assert product.category_label == "Test Category"
    assert product.description == "This is a test product."
    assert product.modified_by == "user@mail.com"


def test_edit_product(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    product = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    db.session.add(product)
    db.session.commit()

    response = client.get(f"/product/{product.id}/edit")
    assert response.status_code == 200

    response = client.post(
        f"/product/{product.id}/edit",
        data={
            "name": "Updated Product Name",
            "category_label": "Updated Category",
            "description": "This is an updated product.",
            "quantity_available": 10,
        },
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )

    assert b"Product updated successfully!" in response.data

    updated_product = db.session.get(Product, product.id)
    assert updated_product.name == "Updated Product Name"
    assert updated_product.category_label == "Updated Category"
    assert updated_product.description == "This is an updated product."
    assert updated_product.quantity_available == 0
    assert updated_product.modified_by == "user@mail.com"


def test_delete_product(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    product = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    db.session.add(product)
    db.session.commit()

    response = client.post(
        f"/product/{product.id}/delete", headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"}, follow_redirects=True
    )
    assert b"Product deleted successfully!" in response.data

    deleted_product = db.session.get(Product, product.id)
    assert deleted_product.deleted is True
    assert deleted_product.modified_by == "user@mail.com"


def test_get_products(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    product_a = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    product_b = Product(
        name="Test Other Product",
        category_label="Other Category",
        description="This is another test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    product_c = Product(
        name="Deleted Product",
        category_label="Deleted Category",
        description="This is a deleted product.",
        quantity_available=0,
        modified_by="test@gmail.com",
        deleted=True,
    )
    db.session.add(product_a)
    db.session.add(product_b)
    db.session.add(product_c)
    db.session.commit()

    response = client.get("/product/get?query=", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 2
    assert data[0]["name"] == "Test Product"
    assert data[1]["name"] == "Test Other Product"

    for product in data:
        assert not product["deleted"]


def test_get_products_with_filter(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    product_a = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    product_b = Product(
        name="Test Other Product",
        category_label="Other Category",
        description="This is another test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    product_c = Product(
        name="Deleted Product",
        category_label="Deleted Category",
        description="This is a deleted product.",
        quantity_available=0,
        modified_by="test@gmail.com",
        deleted=True,
    )
    db.session.add(product_a)
    db.session.add(product_b)
    db.session.add(product_c)
    db.session.commit()

    response = client.get("/product/get?query=Other", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Other Product"


# Order


def test_add_order(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testpartner.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    product = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    partner = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )

    db.session.add(product)
    db.session.add(partner)
    db.session.add(warehouse)
    db.session.commit()

    response = client.post(
        "/order/add",
        data={
            "category": "TRANSACTION",
            "product_name": f"{product.name} ({product.id})",
            "partner_name": f"{partner.name} ({partner.id})",
            "warehouse_name": f"{warehouse.name} ({warehouse.id})",
            "quantity": 5,
            "unit_price": 10.0,
            "currency": "USD",
        },
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "user@mail.com"},
        follow_redirects=True,
    )

    assert b"Order added successfully!" in response.data
    order = Order.query.first()
    assert order is not None
    assert order.product_id == product.id
    assert order.partner_id == partner.id
    assert order.warehouse_id == warehouse.id
    assert order.quantity == 5
    assert order.unit_price == 10.0
    assert order.currency == "USD"
    assert order.modified_by == "user@mail.com"
    product = Product.query.first()
    assert product.quantity_available == 5


def test_edit_order(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testpartner.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    product = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    partner = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )

    db.session.add(product)
    db.session.add(partner)
    db.session.add(warehouse)
    db.session.commit()

    order = Order(
        category="Test Category",
        product_id=product.id,
        partner_id=partner.id,
        warehouse_id=warehouse.id,
        quantity=5,
        unit_price=10.0,
        currency="USD",
        modified_by="test@gmail.com",
    )
    db.session.add(order)
    db.session.commit()

    response = client.get(f"/order/{order.id}/edit")
    assert response.status_code == 200
    assert b"Edit Order" in response.data
    assert b"Test Category" in response.data
    assert b"10.0" in response.data


def test_get_orders(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testpartner.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    product = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    partner = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )

    db.session.add(product)
    db.session.add(partner)
    db.session.add(warehouse)
    db.session.commit()

    order_a = Order(
        category="Test Category",
        product_id=product.id,
        partner_id=partner.id,
        warehouse_id=warehouse.id,
        quantity=5,
        unit_price=10.0,
        currency="USD",
        modified_by="test@gmail.com",
    )
    order_b = Order(
        category="Other Category",
        product_id=product.id,
        partner_id=partner.id,
        warehouse_id=warehouse.id,
        quantity=10,
        unit_price=20.0,
        currency="EUR",
        modified_by="test@gmail.com",
    )

    db.session.add(order_a)
    db.session.add(order_b)
    db.session.commit()

    response = client.get("/order/get?query=", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["category"] == "Test Category"
    assert data[1]["category"] == "Other Category"


def test_get_orders_with_filter(client, app):
    client.post("/login", data={"email": "test@example.com", "password": "password"}, follow_redirects=True)

    contact = Contact(
        email="contact@testpartner.com",
        phone_number="123456789",
        modified_by="test@gmail.com",
    )
    address = Address(
        street_address="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="USA",
        modified_by="test@gmail.com",
    )

    db.session.add(contact)
    db.session.add(address)
    db.session.commit()

    product = Product(
        name="Test Product",
        category_label="Test Category",
        description="This is a test product.",
        quantity_available=0,
        modified_by="test@gmail.com",
    )
    partner = Partner(
        name="Test Partner",
        contact_person="John Doe",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )
    warehouse = Warehouse(
        name="Test Warehouse",
        contact_id=Contact.query.first().id,
        address_id=Address.query.first().id,
        modified_by="test@gmail.com",
    )

    db.session.add(product)
    db.session.add(partner)
    db.session.add(warehouse)
    db.session.commit()

    order_a = Order(
        category="Test Category",
        product_id=product.id,
        partner_id=partner.id,
        warehouse_id=warehouse.id,
        quantity=5,
        unit_price=10.0,
        currency="USD",
        modified_by="test@gmail.com",
    )
    order_b = Order(
        category="Other Category",
        product_id=product.id,
        partner_id=partner.id,
        warehouse_id=warehouse.id,
        quantity=10,
        unit_price=20.0,
        currency="EUR",
        modified_by="test@gmail.com",
    )

    db.session.add(order_a)
    db.session.add(order_b)
    db.session.commit()

    response = client.get("/order/get?query=1", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["category"] == "Test Category"
