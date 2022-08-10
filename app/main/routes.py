import datetime
from flask import abort, render_template, request
from itsdangerous import BadSignature
from app.auth.utils import admin_required, load_user, require_login
from app.models import Expenses, OperatingExpenses, Payment, Plan, Report, User
from app.main import main_bp
from sqlalchemy import extract, and_, func

from app.utils import extract_date, loads_token
from app.models import db


@main_bp.route('/dashboard/')
@require_login
@admin_required
def dashboard():
    gross_sales = db.session.query(db.func.sum(Plan.price)).join(Payment).filter(
        and_(*extract_date(Payment.date_paid, filter_date=request.args.get('filter')))).first()[0]
    
    expenses = db.session.query(db.func.sum(Expenses.amount)).filter(
        and_(*extract_date(Expenses.date_reported, filter_date=request.args.get('filter')))).first()[0]
    
    net_sales = gross_sales - expenses
    net_sales_status = "{:,.2f}".format((net_sales / (Payment.total_sales() - Expenses.total_expenses())) * 100)
    
    op_expenses = db.session.query(OperatingExpenses.name, db.func.sum(Expenses.amount)).join(Expenses).filter(
        and_(*extract_date(Expenses.date_reported, filter_date=request.args.get('filter')))).group_by(OperatingExpenses).all()
    
    total_op_expenses = db.session.query(db.func.sum(Expenses.amount)).filter(
        and_(*extract_date(Expenses.date_reported, filter_date=request.args.get('filter')))
    ).first()
    
    context = dict(
        total_users=len(User.query.all()),
        active_users=len(User.query.join(Payment, Payment.user_id == User.id).all()),
        net_sales=net_sales,
        net_sales_status=float(net_sales_status),
        gross_sales=Payment.sales_data(),
        plan_data=Plan.plan_data(),
        payments=Payment.query.order_by(Payment.date_paid.desc()).limit(5).all(),
        users=User.query.join(User.payments).filter(User.is_active==True).all(),
        reports=Report.query.order_by(Report.date_reported.desc()).limit(5).all(),
        op_expenses=op_expenses,
        total_expenses=sum(total_op_expenses),
        expenses_data=Expenses.expenses_data(),
        )
    
    return render_template('main/dashboard.html', **context)


@main_bp.route("/profile/", defaults={"token": None})
@main_bp.route("/profile/<token>/")
@require_login
def profile(token):
    user = load_user()
    if token:
        try:
            username = loads_token(token, salt="username")
            user = User.query.filter_by(username=username).first()
        except BadSignature:
            return abort(401)
    return render_template("main/profile.html", user=user)


@main_bp.route("/reports/", defaults={'page': 1})
@main_bp.route("/reports/<int:page>/")
@require_login
@admin_required
def report_lists(page):
    reports = Report.query.order_by(Report.date_reported.desc()).paginate(page=page, error_out=False, per_page=2)
    context = dict(
        reports=reports
    )
    return render_template('main/reports.html', **context)