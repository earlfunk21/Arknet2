from flask import jsonify
from app.api import api_bp
from app.models import db, User

import datetime


@api_bp.route("/inactive_users")
def inactive_users():
    users = db.session.query(User).filter(User.id != 1).join(User.payments).all()
    data = []
    for user in users:
        if user.recent_payment.is_expired == True and user.recent_payment.due_date + datetime.timedelta(days=7) > datetime.datetime.now():
            data.append(dict(username=user.username))
    return jsonify(*data)


@api_bp.route("/almost_expired_users")
def almost_expired_users():
    users = db.session.query(User).filter(User.id != 1).join(User.payments).all()
    data = []
    for user in users:
        if user.recent_payment.due_date - datetime.timedelta(days=3) < datetime.datetime.now() and not user.recent_payment.is_expired:
            data.append(dict(username=user.username, date=user.recent_payment.due_date.strftime("%Y-%m-%d")))
    return jsonify(*data)