from flask_wtf import FlaskForm
from wtforms import TextAreaField, FileField, PasswordField, validators, DecimalField
from wtforms.fields.datetime import DateTimeLocalField
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Plan, User
from flask_wtf.file import FileAllowed
from flask import current_app
from datetime import datetime


class PaymentForm(FlaskForm):
    remarks = TextAreaField("Remarks")
    plan = QuerySelectField("Plans", query_factory=lambda: Plan.query, allow_blank=True, validators=[validators.DataRequired()])
    user = QuerySelectField("Users", query_factory=lambda: User.query, get_label='username', allow_blank=True, validators=[validators.DataRequired()])
    due_date = DateTimeLocalField("Due Date", default=datetime.now())
    date_paid = DateTimeLocalField("Date Paid", default=datetime.now())
    total = DecimalField("Total Payment", places=2)
    receipt = FileField('Proof of Payment', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    admin_key = PasswordField("Secret Key", validators=[validators.InputRequired()])
    
    def validate_admin_key(form, field):
        if field.data != current_app.config.get('ADMIN_KEY'):
            raise validators.ValidationError(f"Secret key is incorrect")
