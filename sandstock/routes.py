import re

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from sandstock.forms import (
    CreateOrderForm,
    CreatePartnerForm,
    CreateProductForm,
    CreateWarehouseForm,
    LoginForm,
    RegisterForm,
    UpdateOrderForm,
    UpdatePartnerForm,
    UpdateProductForm,
    UpdateWarehouseForm,
)
from sandstock.models import Address, Contact, Order, Partner, Product, User, Warehouse, db


def register_routes(app: Flask):

    # Login/Logout

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash("Email already exists!", "danger")
            else:
                new_user = User(
                    username=form.username.data,
                    email=form.email.data,
                )
                new_user.set_password(form.password.data)
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully!", "success")
                return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash("Logged in successfully!", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid email or password!", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out!", "success")
        return redirect(url_for("login"))

    @app.route("/")
    # @login_required
    def home():
        orders = Order.query.filter_by().limit(10).all()
        partners = Partner.query.filter_by(deleted=False).limit(10).all()
        warehouses = Warehouse.query.filter_by(deleted=False).limit(10).all()
        products = Product.query.filter_by(deleted=False).limit(10).all()
        return render_template("home.html", partners=partners, warehouses=warehouses, products=products, orders=orders)

    # Partner

    @app.route("/partner/add", methods=["GET", "POST"])
    # @login_required
    def add_partner():
        form = CreatePartnerForm()
        if form.validate_on_submit():
            contact = Contact(email=form.email.data, phone_number=form.phone_number.data)
            db.session.add(contact)
            db.session.commit()

            address = Address(
                street_address=form.street_address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data,
            )
            db.session.add(address)
            db.session.commit()

            partner = Partner(
                name=form.name.data,
                contact_person=form.contact_person.data,
                address_id=address.id,
                contact_id=contact.id,
            )
            db.session.add(partner)
            db.session.commit()

            flash("Partner added successfully!", "success")
            return redirect(url_for("add_partner"))

        return render_template("add_partner.html", form=form)

    @app.route("/partner/<int:partner_id>/edit", methods=["GET", "POST"])
    # @login_required
    def edit_partner(partner_id):
        partner = Partner.query.get_or_404(partner_id)
        contact = Contact.query.get_or_404(partner.contact_id)
        address = Address.query.get_or_404(partner.address_id)

        form = UpdatePartnerForm(
            name=partner.name,
            contact_person=partner.contact_person,
            email=contact.email,
            phone_number=contact.phone_number,
            street_address=address.street_address,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,
            created_at=partner.created_at,
            updated_at=partner.updated_at,
        )

        if form.validate_on_submit():
            partner.name = form.name.data
            partner.contact_person = form.contact_person.data

            contact.email = form.email.data
            contact.phone_number = form.phone_number.data

            address.street_address = form.street_address.data
            address.city = form.city.data
            address.state = form.state.data
            address.postal_code = form.postal_code.data
            address.country = form.country.data

            db.session.commit()
            flash("Partner updated successfully!", "success")
            return redirect(url_for("edit_partner", partner_id=partner.id))

        return render_template("edit_partner.html", form=form, partner=partner)

    @app.route("/partner/<int:partner_id>/delete", methods=["POST"])
    # @login_required
    def delete_partner(partner_id):
        partner = Partner.query.get_or_404(partner_id)
        partner.deleted = True
        db.session.commit()
        flash("Partner deleted successfully!", "success")
        return redirect(url_for("home"))

    @app.route("/partner/get", methods=["GET"])
    # @login_required
    def get_partners():
        query = request.args.get("query", "")
        results = Partner.query.filter(Partner.name.ilike(f"%{query}%"), Partner.deleted == False).limit(10).all()
        partners = [
            {
                "id": partner.id,
                "name": partner.name,
                "contact_person": partner.contact_person,
                "address_id": partner.address_id,
                "contact_id": partner.contact_id,
                "created_at": partner.created_at,
                "updated_at": partner.updated_at,
                "deleted": partner.deleted,
            }
            for partner in results
        ]
        return jsonify(partners)

    # Warehouse

    @app.route("/warehouse/add", methods=["GET", "POST"])
    # @login_required
    def add_warehouse():
        form = CreateWarehouseForm()
        if form.validate_on_submit():
            contact = Contact(email=form.email.data, phone_number=form.phone_number.data)
            db.session.add(contact)
            db.session.commit()

            address = Address(
                street_address=form.street_address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data,
            )
            db.session.add(address)
            db.session.commit()

            warehouse = Warehouse(name=form.name.data, address_id=address.id, contact_id=contact.id)
            db.session.add(warehouse)
            db.session.commit()

            flash("Warehouse added successfully!", "success")
            return redirect(url_for("add_warehouse"))

        return render_template("add_warehouse.html", form=form)

    @app.route("/warehouse/<int:warehouse_id>/edit", methods=["GET", "POST"])
    # @login_required
    def edit_warehouse(warehouse_id):
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        contact = Contact.query.get_or_404(warehouse.contact_id)
        address = Address.query.get_or_404(warehouse.address_id)
        form = UpdateWarehouseForm(
            name=warehouse.name,
            email=contact.email,
            phone_number=contact.phone_number,
            street_address=address.street_address,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )

        if form.validate_on_submit():
            warehouse.name = form.name.data
            contact.email = form.email.data
            contact.phone_number = form.phone_number.data
            address.street_address = form.street_address.data
            address.city = form.city.data
            address.state = form.state.data
            address.postal_code = form.postal_code.data
            address.country = form.country.data
            db.session.commit()
            flash("Warehouse updated successfully!", "success")
            return redirect(url_for("edit_warehouse", warehouse_id=warehouse.id))

        return render_template("edit_warehouse.html", form=form, warehouse=warehouse)

    @app.route("/warehouse/<int:warehouse_id>/delete", methods=["POST"])
    # @login_required
    def delete_warehouse(warehouse_id):
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        warehouse.deleted = True
        db.session.commit()
        flash("Warehouse deleted successfully!", "success")
        return redirect(url_for("home"))

    @app.route("/warehouse/get", methods=["GET"])
    # @login_required
    def get_warehouses():
        query = request.args.get("query", "")
        results = Warehouse.query.filter(Warehouse.name.ilike(f"%{query}%"), Warehouse.deleted == False).limit(10).all()
        warehouses = [
            {
                "id": warehouse.id,
                "name": warehouse.name,
                "address_id": warehouse.address_id,
                "contact_id": warehouse.contact_id,
                "created_at": warehouse.created_at,
                "updated_at": warehouse.updated_at,
                "deleted": warehouse.deleted,
            }
            for warehouse in results
        ]
        return jsonify(warehouses)

    # Product

    @app.route("/product/add", methods=["GET", "POST"])
    # @login_required
    def add_product():
        form = CreateProductForm()
        if form.validate_on_submit():
            product = Product(
                name=form.name.data,
                category_label=form.category_label.data,
                description=form.description.data,
                quantity_available=0,
            )
            db.session.add(product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("add_product"))
        return render_template("add_product.html", form=form)

    @app.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
    # @login_required
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)
        form = UpdateProductForm(obj=product)
        if form.validate_on_submit():
            product.name = form.name.data
            product.category_label = form.category_label.data
            product.description = form.description.data
            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("edit_product", product_id=product.id))
        return render_template("edit_product.html", form=form, product=product)

    @app.route("/product/<int:product_id>/delete", methods=["POST"])
    # @login_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        product.deleted = True
        db.session.commit()
        flash("Product deleted successfully!", "success")
        return redirect(url_for("home"))

    @app.route("/product/get", methods=["GET"])
    # @login_required
    def get_products():
        query = request.args.get("query", "")
        results = Product.query.filter(Product.name.ilike(f"%{query}%"), Product.deleted == False).limit(10).all()
        products = [
            {
                "id": product.id,
                "name": product.name,
                "category_label": product.category_label,
                "description": product.description,
                "quantity_available": product.quantity_available,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "deleted": product.deleted,
            }
            for product in results
        ]
        return jsonify(products)

    # Order

    @app.route("/order/add", methods=["GET", "POST"])
    # @login_required
    def add_order():
        form = CreateOrderForm()
        form.product_name.choices = [
            f"{product.name} ({product.id})" for product in Product.query.filter_by(deleted=False).limit(10).all()
        ]
        form.partner_name.choices = [
            f"{partner.name} ({partner.id})" for partner in Partner.query.filter_by(deleted=False).limit(10).all()
        ]
        form.warehouse_name.choices = [
            f"{warehouse.name} ({warehouse.id})"
            for warehouse in Warehouse.query.filter_by(deleted=False).limit(10).all()
        ]

        if form.validate_on_submit():
            regex = "(.+?) \((\d+)\)$"
            product_id = re.match(regex, form.product_name.data).group(2)
            partner_id = re.match(regex, form.partner_name.data).group(2)
            warehouse_id = re.match(regex, form.warehouse_name.data).group(2)

            order = Order(
                category=form.category.data,
                product_id=product_id,
                partner_id=partner_id,
                warehouse_id=warehouse_id,
                quantity=form.quantity.data,
                unit_price=form.unit_price.data,
                currency=form.currency.data,
            )
            db.session.add(order)
            db.session.commit()
            flash("Order added successfully!", "success")
            return redirect(url_for("add_order"))

        return render_template("add_order.html", form=form)

    @app.route("/order/get", methods=["GET"])
    # @login_required
    def get_orders():
        query = request.args.get("query", "")
        results = Order.query.filter(Order.id.ilike(f"%{query}%")).limit(10).all()
        orders = [
            {
                "id": order.id,
                "category": order.category,
                "product_id": order.product_id,
                "partner_id": order.partner_id,
                "warehouse_id": order.warehouse_id,
                "quantity": order.quantity,
                "unit_price": order.unit_price,
                "currency": order.currency,
                "created_at": order.created_at,
            }
            for order in results
        ]
        return jsonify(orders)

    @app.route("/order/<int:order_id>/edit", methods=["GET"])
    # @login_required
    def edit_order(order_id):
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(order.product_id)
        partner = Partner.query.get_or_404(order.partner_id)
        warehouse = Warehouse.query.get_or_404(order.warehouse_id)

        form = UpdateOrderForm(
            id=order.id,
            category=order.category,
            product_name=product.name,
            partner_name=partner.name,
            warehouse_name=warehouse.name,
            quantity=order.quantity,
            unit_price=order.unit_price,
            currency=order.currency,
            created_at=order.created_at,
        )
        return render_template("edit_order.html", form=form, order=order)
