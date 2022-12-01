

import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import request, session
from sqlalchemy import extract
import timeago
from app import captcha
from wtforms import ValidationError
import random

from send_email import send_email
s = URLSafeTimedSerializer("arkhnet")


def loads_token(token, max_age=None, salt=None):
    return s.loads(token, max_age, salt=salt)


def dumps_token(token, salt=None):
    return s.dumps(token, salt)


def extract_date(obj_date, filter_date=None):
    sales_extract = [extract('month', obj_date) == datetime.datetime.now().month,
                     extract('year', obj_date) == datetime.datetime.now().year]
    if filter_date == 'Year':
        sales_extract.pop(0)
    return sales_extract


def time_ago(date):
    return timeago.format(date, datetime.datetime.now())


def captcha_validator(form, field):
    if not captcha.validate(field.data):
        raise ValidationError('Invalid Captcha')

def check_code(code):
    return code == session.get('verification_code')