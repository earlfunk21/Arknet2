from flask import Blueprint


plan_bp = Blueprint("plan", __name__, url_prefix='/plan')


from app.plan import routes