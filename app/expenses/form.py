from flask_wtf import FlaskForm
from wtforms import IntegerField, FileField, PasswordField, validators, StringField
from flask_wtf.file import FileAllowed
from flask import current_app


class ExpensesForm(FlaskForm):
    name = StringField("Name of Expenses", validators=[validators.InputRequired()])
    cost = IntegerField("Cost", default=0)
    receipt = FileField('Proof of Payment', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    admin_key = PasswordField("Secret Key", validators=[validators.InputRequired()])
    
    def validate_admin_key(form, field):
        if field.data != current_app.config.get('ADMIN_KEY'):
            raise validators.ValidationError(f"Secret key is incorrect")