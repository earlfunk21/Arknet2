from flask_wtf import FlaskForm
from wtforms import validators, StringField, TextAreaField
from app.utils import captcha_validator
        
class ReportForm(FlaskForm):
    subject = StringField("Subject", validators=[validators.DataRequired()])
    message = TextAreaField("Message")
    captcha = StringField("Captcha", validators=[captcha_validator])
