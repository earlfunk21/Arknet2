from flask_wtf import FlaskForm, RecaptchaField
from wtforms import IntegerField, validators, PasswordField
from flask import current_app


class CreatePlanForm(FlaskForm):
    
    price = IntegerField("Price", validators=[validators.InputRequired()])
    speed = IntegerField("Speed", validators=[validators.InputRequired()])
    admin_key = PasswordField("Secret Key", validators=[validators.InputRequired()])
    
    def validate_admin_key(form, field):
        if field.data != current_app.config.get('ADMIN_KEY'):
            raise validators.ValidationError(f"Secret key is incorrect")