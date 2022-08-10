from flask import Blueprint


payment_bp = Blueprint("payment", __name__, url_prefix='/payment')


from app.payment import routes, forms