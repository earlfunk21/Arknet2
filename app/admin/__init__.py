
from flask import Blueprint


admin_bp = Blueprint("admin", __name__, cli_group=None)

from app.admin import routes
from app import payment, plan

admin_bp.register_blueprint(payment.payment_bp)
admin_bp.register_blueprint(plan.plan_bp)