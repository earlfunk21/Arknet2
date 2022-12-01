from flask import jsonify, session
from app.api import api_bp
from app.models import db, User, Payment

import datetime

import random

from send_email import send_email


@api_bp.route("/inactive_users")
def inactive_users():
    users = db.session.query(User).filter(User.id != 1).join(User.payments).join(User.email_address).all()
    emails = []
    for user in users:
        if user.recent_payment.is_expired == True and user.recent_payment.due_date + datetime.timedelta(days=7) > datetime.datetime.now():
            emails.append(user.email_address.email)
    return jsonify(emails)
