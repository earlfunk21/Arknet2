from flask_wtf import FlaskForm
from wtforms import FloatField, PasswordField, validators, StringField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import OperatingExpenses
from flask import current_app

from app.utils import captcha_validator


class ExpensesForm(FlaskForm):
    amount = FloatField("Amount of Expenses")
    op_expenses = QuerySelectField("Operating Expenses", query_factory=lambda: OperatingExpenses.query, get_label="name")
    
    admin_key = PasswordField("Secret Key", validators=[validators.InputRequired()])
    
    def validate_admin_key(form, field):
        if field.data != current_app.config.get('ADMIN_KEY'):
            raise validators.ValidationError(f"Secret key is incorrect")
        
class ReportForm(FlaskForm):
    subject = StringField("Subject", validators=[validators.DataRequired()])
    message = TextAreaField("Message")
    captcha = StringField("Captcha", validators=[captcha_validator])
