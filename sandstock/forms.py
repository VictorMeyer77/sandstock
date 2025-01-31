from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match!")
    ])
    submit = SubmitField("Register")


class PartnerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    contact_person = StringField("Contact Person")
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number")
    street_address = StringField("Street Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    postal_code = StringField("Postal Code", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    submit = SubmitField("Add Partner")

class ProductForm(FlaskForm):
    new_category = StringField("New Category")
    new_supplier = StringField("New Supplier")
    supplier_contact = StringField("Supplier Contact Info")
    new_product = StringField("New Product", validators=[DataRequired()])
    product_price = IntegerField("Product Price", validators=[DataRequired()])
    submit = SubmitField("Add Product")

class TransactionForm(FlaskForm):
    product_id = SelectField("Product", coerce=int, validators=[DataRequired()])
    transaction_type = SelectField("Transaction Type", choices=[("IN", "IN"), ("OUT", "OUT")], validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Add Transaction")

    def validate_quantity(self, field):
        if field.data <= 0:
            raise ValidationError("Quantity must be greater than 0.")
