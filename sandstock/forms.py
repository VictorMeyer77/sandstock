from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateTimeLocalField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match!")]
    )
    submit = SubmitField("Register")


class CreatePartnerForm(FlaskForm):
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


class UpdatePartnerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    contact_person = StringField("Contact Person", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number")
    street_address = StringField("Street Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    postal_code = StringField("Postal Code", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    created_at = DateTimeLocalField("Created At", format="%Y-%m-%dT%H:%M", render_kw={"readonly": True})
    updated_at = DateTimeLocalField("Updated At", format="%Y-%m-%dT%H:%M", render_kw={"readonly": True})
    submit = SubmitField("Update Partner")


class CreateWarehouseForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number")
    street_address = StringField("Street Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    postal_code = StringField("Postal Code", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    submit = SubmitField("Add Warehouse")


class UpdateWarehouseForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number")
    street_address = StringField("Street Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    postal_code = StringField("Postal Code", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    created_at = DateTimeLocalField("Created At", format="%Y-%m-%dT%H:%M", render_kw={"readonly": True})
    updated_at = DateTimeLocalField("Updated At", format="%Y-%m-%dT%H:%M", render_kw={"readonly": True})
    submit = SubmitField("Update Warehouse")


class CreateProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    category_label = StringField("Category Label", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Add Product")


class UpdateProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    category_label = StringField("Category Label", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    quantity_available = IntegerField("Quantity Available", validators=[DataRequired()], render_kw={"readonly": True})
    created_at = DateTimeLocalField("Created At", format="%Y-%m-%dT%H:%M", render_kw={"readonly": True})
    updated_at = DateTimeLocalField("Updated At", format="%Y-%m-%dT%H:%M", render_kw={"readonly": True})
    submit = SubmitField("Update Product")


class CreateOrderForm(FlaskForm):
    category = SelectField(
        "Category", choices=[("TRANSACTION", "TRANSACTION"), ("CORRECTION", "CORRECTION")], validators=[DataRequired()]
    )
    product_name = SelectField("Product", coerce=str, validators=[DataRequired()])
    partner_name = SelectField("Partner", coerce=str, validators=[DataRequired()])
    warehouse_name = SelectField("Warehouse", coerce=str, validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    unit_price = FloatField("Unit Price")
    currency = SelectField("Currency", choices=[("USD", "USD"), ("EUR", "EUR")], validators=[DataRequired()])
    submit = SubmitField("Add Order")

    def validate_unit_price(self, field):
        if field.data < 0.0:
            raise ValidationError("Price must be greater or equal than 0.")


class UpdateOrderForm(FlaskForm):
    id = IntegerField("ID", render_kw={"readonly": True})
    category = StringField("Category", validators=[DataRequired()], render_kw={"readonly": True})
    product_name = StringField("Product", validators=[DataRequired()], render_kw={"readonly": True})
    partner_name = StringField("Partner", validators=[DataRequired()], render_kw={"readonly": True})
    warehouse_name = StringField("Warehouse", validators=[DataRequired()], render_kw={"readonly": True})
    quantity = IntegerField("Quantity", validators=[DataRequired()], render_kw={"readonly": True})
    unit_price = FloatField("Unit Price", validators=[DataRequired()], render_kw={"readonly": True})
    currency = StringField("Currency", validators=[DataRequired()], render_kw={"readonly": True})
    created_at = DateTimeLocalField("Created At", format="%Y-%m-%dT%H:%M", render_kw={"readonly": True})
    submit = SubmitField("Update Order", render_kw={"disabled": True})
