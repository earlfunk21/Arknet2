from flask import Blueprint


expenses_bp = Blueprint("expenses", __name__, url_prefix='/expenses')


from app.expenses import routes, form