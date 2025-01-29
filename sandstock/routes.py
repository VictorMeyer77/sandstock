from flask import Flask, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from sandstock.models import db, User, Transaction, Product, Category, Supplier
from sandstock.forms import RegisterForm, LoginForm, TransactionForm, ProductForm


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

    # Business

    @app.route("/")
    @login_required
    def home():
        transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(20).all()
        return render_template("home.html", transactions=transactions)

    @app.route("/add-product", methods=["GET", "POST"])
    @login_required
    def add_product():
        form = ProductForm()

        if form.validate_on_submit():
            category = None
            supplier = None

            if form.new_category.data:
                category = Category(name=form.new_category.data)
                db.session.add(category)
                db.session.commit()
                flash(f"Category '{category.name}' added!", "success")

            if form.new_supplier.data:
                supplier = Supplier(name=form.new_supplier.data, contact_info=form.supplier_contact.data)
                db.session.add(supplier)
                db.session.commit()
                flash(f"Supplier '{supplier.name}' added!", "success")

            product = Product(
                name=form.new_product.data,
                price=form.product_price.data,
                category_id=category.id if category else None,
                supplier_id=supplier.id if supplier else None,
                stock_quantity=0
            )

            db.session.add(product)
            db.session.commit()
            flash(f"Product '{product.name}' added!", "success")
            return redirect(url_for("home"))

        return render_template("add_product.html", form=form)

    @app.route("/add-transaction", methods=["GET", "POST"])
    @login_required
    def add_transaction():
        form = TransactionForm()
        form.product_id.choices = [(p.id, p.name) for p in Product.query.all()]

        if form.validate_on_submit():
            product = Product.query.get(form.product_id.data)
            if form.transaction_type.data == "IN":
                product.stock_quantity += form.quantity.data
            elif form.transaction_type.data == "OUT":
                if product.stock_quantity < form.quantity.data:
                    flash(f"Not enough stock for '{product.name}'!", "danger")
                    return redirect(url_for("add_transaction"))
                product.stock_quantity -= form.quantity.data

            transaction = Transaction(
                product_id=form.product_id.data,
                transaction_type=form.transaction_type.data,
                quantity=form.quantity.data,
            )

            db.session.add(transaction)
            db.session.commit()
            flash("Transaction added successfully!", "success")
            return redirect(url_for("home"))

        return render_template("add_transaction.html", form=form)


