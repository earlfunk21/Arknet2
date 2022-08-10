from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextAreaField, IntegerField
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Plan, User, UserDetails


class PaymentForm(FlaskForm):
    remarks = TextAreaField("Remarks")
    plan = QuerySelectField("Plans", query_factory=lambda: Plan.query)
    user = QuerySelectField("Users", query_factory=lambda: User.query, get_label='username')
    days = IntegerField("Days", default=0)
    months = IntegerField("Months", default=0)
    years = IntegerField("Years", default=0)