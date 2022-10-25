
from flask import Blueprint, abort, request

from app.auth.utils import require_login


admin_bp = Blueprint("admin", __name__, cli_group=None)

from app.admin import routes
from app import payment, plan, expenses

@admin_bp.before_request
@require_login
def check_is_admin():
    from app.auth.utils import load_user

    token = request.args.get('token')
    if not load_user().is_admin and not token:
        return abort(401)

admin_bp.register_blueprint(payment.payment_bp)
admin_bp.register_blueprint(plan.plan_bp)
admin_bp.register_blueprint(expenses.expenses_bp)