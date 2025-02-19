import re
from urllib.parse import urlencode

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import String, cast

from sandstock import Config
from sandstock.forms import (
    CreateOrderForm,
    CreatePartnerForm,
    CreateProductForm,
    CreateWarehouseForm,
    UpdateOrderForm,
    UpdatePartnerForm,
    UpdateProductForm,
    UpdateWarehouseForm,
)
from sandstock.models import Address, Contact, Order, Partner, Product, Warehouse, db


def register_routes(app: Flask):

    @app.route("/logout")
    def logout():
        params = {
            "post_logout_redirect_uri": Config.POST_LOGOUT_URL,
            "client_id": request.headers.get("X-MS-CLIENT-PRINCIPAL-ID", "unknown"),
        }
        return redirect(f"{Config.LOGOUT_URL}?{urlencode(params)}")

    @app.route("/")
    def home():
        orders = db.session.query(Order).limit(10).all()
        partners = db.session.query(Partner).filter_by(deleted=False).limit(10).all()
        warehouses = db.session.query(Warehouse).filter_by(deleted=False).limit(10).all()
        products = db.session.query(Product).filter_by(deleted=False).limit(10).all()
        return render_template("home.html", partners=partners, warehouses=warehouses, products=products, orders=orders)

    # Partner

    @app.route("/partner/add", methods=["GET", "POST"])
    def add_partner():
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")
        form = CreatePartnerForm()
        if form.validate_on_submit():
            contact = Contact(email=form.email.data, phone_number=form.phone_number.data, modified_by=user_email)
            db.session.add(contact)

            address = Address(
                street_address=form.street_address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data,
                modified_by=user_email,
            )
            db.session.add(address)
            db.session.commit()

            partner = Partner(
                name=form.name.data,
                contact_person=form.contact_person.data,
                address_id=address.id,
                contact_id=contact.id,
                modified_by=user_email,
            )
            db.session.add(partner)
            db.session.commit()

            flash("Partner added successfully!", "success")
            return redirect(url_for("add_partner"))

        return render_template("add_partner.html", form=form)

    @app.route("/partner/<int:partner_id>/edit", methods=["GET", "POST"])
    def edit_partner(partner_id):
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")

        partner = db.session.get(Partner, partner_id)
        if not partner:
            flash("Partner not found!", "error")
            return redirect(url_for("home"))

        contact = db.session.get(Contact, partner.contact_id)
        address = db.session.get(Address, partner.address_id)

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
            modified_by=partner.modified_by,
        )

        if form.validate_on_submit():
            partner.name = form.name.data
            partner.contact_person = form.contact_person.data
            partner.modified_by = user_email

            contact.email = form.email.data
            contact.phone_number = form.phone_number.data
            contact.modified_by = user_email

            address.street_address = form.street_address.data
            address.city = form.city.data
            address.state = form.state.data
            address.postal_code = form.postal_code.data
            address.country = form.country.data
            address.modified_by = user_email

            db.session.commit()
            flash("Partner updated successfully!", "success")
            return redirect(url_for("edit_partner", partner_id=partner.id))

        return render_template("edit_partner.html", form=form, partner=partner)

    @app.route("/partner/<int:partner_id>/delete", methods=["POST"])
    def delete_partner(partner_id):
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")

        partner = db.session.get(Partner, partner_id)
        if not partner:
            flash("Partner not found!", "error")
            return redirect(url_for("home"))

        partner.deleted = True
        partner.modified_by = user_email
        db.session.commit()
        flash("Partner deleted successfully!", "success")
        return redirect(url_for("home"))

    @app.route("/partner/get", methods=["GET"])
    def get_partners():
        query = request.args.get("query", "")

        results = (
            db.session.query(Partner)
            .filter(Partner.name.ilike(f"%{query}%"), Partner.deleted == False)  # type: ignore # noqa: E712
            .limit(10)
            .all()
        )
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
    def add_warehouse():
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")
        form = CreateWarehouseForm()
        if form.validate_on_submit():
            contact = Contact(email=form.email.data, phone_number=form.phone_number.data, modified_by=user_email)
            db.session.add(contact)
            db.session.commit()

            address = Address(
                street_address=form.street_address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data,
                modified_by=user_email,
            )
            db.session.add(address)
            db.session.commit()

            warehouse = Warehouse(
                name=form.name.data, address_id=address.id, contact_id=contact.id, modified_by=user_email
            )
            db.session.add(warehouse)
            db.session.commit()

            flash("Warehouse added successfully!", "success")
            return redirect(url_for("add_warehouse"))

        return render_template("add_warehouse.html", form=form)

    @app.route("/warehouse/<int:warehouse_id>/edit", methods=["GET", "POST"])
    def edit_warehouse(warehouse_id):
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")

        warehouse = db.session.get(Warehouse, warehouse_id)
        if not warehouse:
            flash("Warehouse not found!", "error")
            return redirect(url_for("home"))

        contact = db.session.get(Contact, warehouse.contact_id)
        address = db.session.get(Address, warehouse.address_id)

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
            modified_by=warehouse.modified_by,
        )

        if form.validate_on_submit():
            warehouse.name = form.name.data
            warehouse.modified_by = user_email

            contact.email = form.email.data
            contact.phone_number = form.phone_number.data
            contact.modified_by = user_email

            address.street_address = form.street_address.data
            address.city = form.city.data
            address.state = form.state.data
            address.postal_code = form.postal_code.data
            address.country = form.country.data
            address.modified_by = user_email

            db.session.commit()
            flash("Warehouse updated successfully!", "success")
            return redirect(url_for("edit_warehouse", warehouse_id=warehouse.id))

        return render_template("edit_warehouse.html", form=form, warehouse=warehouse)

    @app.route("/warehouse/<int:warehouse_id>/delete", methods=["POST"])
    def delete_warehouse(warehouse_id):
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")

        warehouse = db.session.get(Warehouse, warehouse_id)
        if not warehouse:
            flash("Warehouse not found!", "error")
            return redirect(url_for("home"))

        warehouse.deleted = True
        warehouse.modified_by = user_email
        db.session.commit()
        flash("Warehouse deleted successfully!", "success")
        return redirect(url_for("home"))

    @app.route("/warehouse/get", methods=["GET"])
    def get_warehouses():
        query = request.args.get("query", "")
        results = (
            db.session.query(Warehouse)
            .filter(Warehouse.name.ilike(f"%{query}%"), Warehouse.deleted == False)  # type: ignore # noqa: E712
            .limit(10)
            .all()
        )
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
    def add_product():
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")
        form = CreateProductForm()
        if form.validate_on_submit():
            product = Product(
                name=form.name.data,
                category_label=form.category_label.data,
                description=form.description.data,
                quantity_available=0,
                modified_by=user_email,
            )
            db.session.add(product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("add_product"))
        return render_template("add_product.html", form=form)

    @app.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
    def edit_product(product_id):
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")

        product = db.session.get(Product, product_id)
        if not product:
            flash("Product not found!", "error")
            return redirect(url_for("home"))

        form = UpdateProductForm(
            name=product.name,
            category_label=product.category_label,
            description=product.description,
            quantity_available=product.quantity_available,
            created_at=product.created_at,
            updated_at=product.updated_at,
            modified_by=product.modified_by,
        )

        if form.validate_on_submit():
            product.name = form.name.data
            product.category_label = form.category_label.data
            product.description = form.description.data
            product.modified_by = user_email
            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("edit_product", product_id=product.id))
        return render_template("edit_product.html", form=form, product=product)

    @app.route("/product/<int:product_id>/delete", methods=["POST"])
    def delete_product(product_id):
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")

        product = db.session.get(Product, product_id)
        if not product:
            flash("Product not found!", "error")
            return redirect(url_for("home"))

        product.deleted = True
        product.modified_by = user_email
        db.session.commit()
        flash("Product deleted successfully!", "success")
        return redirect(url_for("home"))

    @app.route("/product/get", methods=["GET"])
    def get_products():
        query = request.args.get("query", "")

        results = (
            db.session.query(Product)
            .filter(Product.name.ilike(f"%{query}%"), Product.deleted == False)  # type: ignore # noqa: E712
            .limit(10)
            .all()
        )
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
    def add_order():
        user_email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "unknown")
        form = CreateOrderForm()
        form.product_name.choices = [
            f"{product.name} ({product.id})"
            for product in db.session.query(Product).filter_by(deleted=False).limit(10).all()
        ]
        form.partner_name.choices = [
            f"{partner.name} ({partner.id})"
            for partner in db.session.query(Partner).filter_by(deleted=False).limit(10).all()
        ]
        form.warehouse_name.choices = [
            f"{warehouse.name} ({warehouse.id})"
            for warehouse in db.session.query(Warehouse).filter_by(deleted=False).limit(10).all()
        ]

        if form.validate_on_submit():
            regex = r"(.+?) \((\d+)\)$"
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
                modified_by=user_email,
            )
            product = db.session.get(Product, order.product_id)
            product.quantity_available += order.quantity
            db.session.add(order)
            db.session.commit()
            flash("Order added successfully!", "success")
            return redirect(url_for("add_order"))

        return render_template("add_order.html", form=form)

    @app.route("/order/get", methods=["GET"])
    def get_orders():
        query = request.args.get("query", "")
        results = db.session.query(Order).filter(cast(Order.id, String).ilike(f"%{query}%")).limit(10).all()
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
    def edit_order(order_id):

        order = db.session.get(Order, order_id)
        if not order:
            flash("Order not found!", "error")
            return redirect(url_for("home"))

        product = db.session.get(Product, order.product_id)
        partner = db.session.get(Partner, order.partner_id)
        warehouse = db.session.get(Warehouse, order.warehouse_id)

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
            modified_by=order.modified_by,
        )
        return render_template("edit_order.html", form=form, order=order)
