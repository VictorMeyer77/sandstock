from flask import Flask, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from sandstock.models import db, User, Order, Contact, Address, Partner
from sandstock.forms import RegisterForm, LoginForm, PartnerForm


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
        transactions = Order.query.order_by(Order.created_at.desc()).limit(20).all()
        return render_template("home.html", transactions=transactions)


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