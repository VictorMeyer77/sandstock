from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required
from sandstock.models import db, User, Order, Contact, Address, Partner, Warehouse, Product
from sandstock.forms import RegisterForm, LoginForm, PartnerForm, WarehouseForm, ProductForm


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
    @login_required
    def home():
        partners = Partner.query.limit(20).all()
        warehouses = Warehouse.query.limit(20).all()
        products = Product.query.limit(20).all()
        return render_template("home.html", partners=partners, warehouses=warehouses, products=products)

    @app.route("/add_partner", methods=["GET", "POST"])
    @login_required
    def add_partner():
        form = PartnerForm()
        if form.validate_on_submit():
            contact = Contact(email=form.email.data, phone_number=form.phone_number.data)
            db.session.add(contact)
            db.session.commit()

            address = Address(
                street_address=form.street_address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data
            )
            db.session.add(address)
            db.session.commit()

            partner = Partner(
                name=form.name.data,
                contact_person=form.contact_person.data,
                address_id=address.id,
                contact_id=contact.id
            )
            db.session.add(partner)
            db.session.commit()

            flash("Partner added successfully!", "success")
            return redirect(url_for("add_partner"))

        return render_template("add_partner.html", form=form)

    @app.route("/add_warehouse", methods=["GET", "POST"])
    @login_required
    def add_warehouse():
        form = WarehouseForm()
        if form.validate_on_submit():
            contact = Contact(email=form.email.data, phone_number=form.phone_number.data)
            db.session.add(contact)
            db.session.commit()

            address = Address(
                street_address=form.street_address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data
            )
            db.session.add(address)
            db.session.commit()

            warehouse = Warehouse(
                name=form.name.data,
                address_id=address.id,
                contact_id=contact.id
            )
            db.session.add(warehouse)
            db.session.commit()

            flash("Warehouse added successfully!", "success")
            return redirect(url_for("add_warehouse"))

        return render_template("add_warehouse.html", form=form)

    @app.route("/add_product", methods=["GET", "POST"])
    @login_required
    def add_product():
        form = ProductForm()
        if form.validate_on_submit():
            product = Product(
                name=form.name.data,
                category_label=form.category_label.data,
                description=form.description.data,
                quantity_available=0
            )
            db.session.add(product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("add_product"))
        return render_template("add_product.html", form=form)

    @app.route("/search_partners", methods=["GET"])
    def search_partners():
        query = request.args.get("query", "")
        results = Partner.query.filter(Partner.name.ilike(f"%{query}%"), Partner.deleted == False).limit(20).all()
        partners = [
            {
                "id": partner.id,
                "name": partner.name,
                "contact_person": partner.contact_person,
                "address_id": partner.address_id,
                "contact_id": partner.contact_id,
                "created_at": partner.created_at,
                "updated_at": partner.updated_at,
                "deleted": partner.deleted
            }
            for partner in results
        ]
        return jsonify(partners)

    @app.route("/search_warehouses", methods=["GET"])
    def search_warehouses():
        query = request.args.get("query", "")
        results = Warehouse.query.filter(Warehouse.name.ilike(f"%{query}%"), Warehouse.deleted == False).limit(20).all()
        warehouses = [
            {
                "id": warehouse.id,
                "name": warehouse.name,
                "address_id": warehouse.address_id,
                "contact_id": warehouse.contact_id,
                "created_at": warehouse.created_at,
                "updated_at": warehouse.updated_at,
                "deleted": warehouse.deleted
            }
            for warehouse in results
        ]
        return jsonify(warehouses)

    @app.route("/search_products", methods=["GET"])
    def search_products():
        query = request.args.get("query", "")
        results = Product.query.filter(Product.name.ilike(f"%{query}%"), Product.deleted == False).limit(20).all()
        products = [
            {
                "id": product.id,
                "name": product.name,
                "category_label": product.category_label,
                "description": product.description,
                "quantity_available": product.quantity_available,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "deleted": product.deleted
            }
            for product in results
        ]
        return jsonify(products)