import random

from sandstock import User, db
from sandstock.models import Address, Contact, Order, Partner, Product, Warehouse


def run():
    db.drop_all()
    db.create_all()

    user_count = 10
    contact_count = 50
    address_count = 50
    product_count = 100
    partner_count = 50
    warehouse_count = 5
    order_count = 1000

    add_users(user_count)
    add_contacts(contact_count, user_count)
    add_addresses(address_count, user_count)
    add_products(product_count, user_count)
    add_partners(partner_count, user_count, address_count, contact_count)
    add_warehouses(warehouse_count, user_count, address_count, contact_count)
    add_orders(order_count, user_count, product_count, partner_count, warehouse_count)


def add_users(count):
    users = []
    for i in range(count):
        username = f"user {i+1}"
        email = f"{username}@example.com"
        password = "password123"
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        users.append(new_user)
    db.session.commit()
    return users


def add_contacts(count, user_size):
    contacts = []
    for i in range(count):
        email = f"contact{i+1}@example.com"
        phone_number = f"123-456-789{i}"
        modified_by = random.randint(1, user_size)
        new_contact = Contact(email=email, phone_number=phone_number, modified_by=modified_by)
        db.session.add(new_contact)
        contacts.append(new_contact)
    db.session.commit()
    return contacts


def add_addresses(count, user_size):
    addresses = []
    for i in range(count):
        street_address = f"{i+1} Example Street"
        city = f"City{i+1}"
        state = f"State{i+1}"
        postal_code = f"12345{i}"
        country = "Example Country"
        modified_by = random.randint(1, user_size)
        new_address = Address(
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            modified_by=modified_by,
        )
        db.session.add(new_address)
        addresses.append(new_address)
    db.session.commit()
    return addresses


def add_products(count, user_size):
    products = []
    categories = ["Electronics", "Furniture", "Clothing", "Books", "Toys"]
    for i in range(count):
        name = f"Product {i+1}"
        category_label = random.choice(categories)
        description = f"Description for {name}"
        quantity_available = 0
        modified_by = random.randint(1, user_size)
        new_product = Product(
            name=name,
            category_label=category_label,
            description=description,
            quantity_available=quantity_available,
            modified_by=modified_by,
        )
        db.session.add(new_product)
        products.append(new_product)
    db.session.commit()
    return products


def add_partners(count, user_size, address_size, contact_size):
    partners = []
    for i in range(count):
        name = f"Partner {i+1}"
        contact_person = f"Contact Person {i+1}"
        address_id = random.randint(1, address_size)
        contact_id = random.randint(1, contact_size)
        modified_by = random.randint(1, user_size)
        new_partner = Partner(
            name=name,
            contact_person=contact_person,
            address_id=address_id,
            contact_id=contact_id,
            modified_by=modified_by,
        )
        db.session.add(new_partner)
        partners.append(new_partner)
    db.session.commit()
    return partners


def add_warehouses(count, user_size, address_size, contact_size):
    warehouses = []
    for i in range(count):
        name = f"Warehouse {i+1}"
        address_id = random.randint(1, address_size)
        contact_id = random.randint(1, contact_size)
        modified_by = random.randint(1, user_size)
        new_warehouse = Warehouse(name=name, address_id=address_id, contact_id=contact_id, modified_by=modified_by)
        db.session.add(new_warehouse)
        warehouses.append(new_warehouse)
    db.session.commit()
    return warehouses


def add_orders(count, user_size, product_size, partner_size, warehouse_size):
    orders = []
    categories = ["TRANSACTION", "CORRECTION"]
    currencies = ["USD", "EUR"]
    for i in range(count):
        category = random.choice(categories)
        product_id = random.randint(1, product_size)
        partner_id = random.randint(1, partner_size)
        warehouse_id = random.randint(1, warehouse_size)
        quantity = random.randint(1, 200)
        unit_price = round(random.uniform(10.0, 1000.0), 2)
        currency = random.choice(currencies)
        modified_by = random.randint(1, user_size)
        new_order = Order(
            category=category,
            product_id=product_id,
            partner_id=partner_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
            unit_price=unit_price,
            currency=currency,
            modified_by=modified_by,
        )
        product = Product.query.get(new_order.product_id)
        product.quantity_available += new_order.quantity
        db.session.add(new_order)
        orders.append(new_order)
    db.session.commit()
    return orders
