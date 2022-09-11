from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextAreaField, IntegerField, FileField, PasswordField, validators
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Plan, User, UserDetails
from flask_wtf.file import FileAllowed
from flask import current_app


class PaymentForm(FlaskForm):
    remarks = TextAreaField("Remarks")
    plan = QuerySelectField("Plans", query_factory=lambda: Plan.query, allow_blank=True, validators=[validators.DataRequired()])
    user = QuerySelectField("Users", query_factory=lambda: User.query, get_label='username', allow_blank=True, validators=[validators.DataRequired()])
    days = IntegerField("Days", default=0)
    total = IntegerField("Total Payment", default=0)
    receipt = FileField('Proof of Payment', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    admin_key = PasswordField("Secret Key", validators=[validators.InputRequired()])
    
    def validate_admin_key(form, field):
        if field.data != current_app.config.get('ADMIN_KEY'):
            raise validators.ValidationError(f"Secret key is incorrect")