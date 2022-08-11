import datetime
from flask import abort, render_template, request, redirect, url_for
from itsdangerous import BadSignature
from app.auth.utils import admin_required, load_user, require_login
from app.main.form import CapitalForm, ExpensesForm, ReportForm
from app.models import Capital, Expenses, OperatingExpenses, Payment, Plan, Report, User, UserDetails
from app.main import main_bp
from sqlalchemy import and_

from app.utils import extract_date, loads_token
from app.models import db


@main_bp.route('/dashboard/')
@require_login
@admin_required
def dashboard():
    gross_sales = db.session.query(db.func.sum(Plan.price)).join(Payment).filter(
        and_(*extract_date(Payment.date_paid, filter_date=request.args.get('filter')))).first()[0] or 0
    
    capital = Capital.onhand_capital()
    
    net_sales = gross_sales
    if capital < 0:
        net_sales = net_sales + capital
        capital = 0
    
    op_expenses = db.session.query(OperatingExpenses.name, db.func.sum(Expenses.amount)).join(Expenses).filter(
        and_(*extract_date(Expenses.date_reported, filter_date=request.args.get('filter')))).group_by(OperatingExpenses).all()
    
    context = dict(
        capital="{:,.2f}".format(capital),
        active_users=len(User.query.join(Payment, Payment.user_id == User.id).all()),
        net_sales=net_sales,
        gross_sales=Payment.sales_data(),
        plan_data=Plan.plan_data(),
        payments=Payment.query.order_by(Payment.date_paid.desc()).limit(5).all(),
        users=User.query.join(User.payments).filter(User.is_active==True).all(),
        reports=Report.query.order_by(Report.date_reported.desc()).limit(5).all(),
        op_expenses=op_expenses,
        expenses_data=Expenses.expenses_data(),
        )
    
    return render_template('main/dashboard.html', **context)


@main_bp.route("/", defaults={"token": None}, methods=["POST", "GET"])
@main_bp.route("/<token>/")
@require_login
def profile(token):
    user = load_user()
    if token:
        try:
            username = loads_token(token, salt="username")
            user = User.query.filter_by(username=username).first()
        except BadSignature:
            return abort(401)
    if request.method == "POST":
        about = request.form['about']
        phone = request.form['phone']
        company = request.form['company']
        account_name = request.form['account_name']
        user.user_details.about = about
        user.user_details.phone = phone
        user.user_details.social_media.name = company
        user.user_details.social_media.account_name = account_name
        db.session.commit()
        
    return render_template("main/profile.html", user=user)


@main_bp.route("/reports/", defaults={'page': 1})
@main_bp.route("/reports/<int:page>/")
@require_login
@admin_required
def report_lists(page):
    reports = Report.query.order_by(Report.date_reported.desc()).paginate(page=page, error_out=False, per_page=10)
    context = dict(
        reports=reports
    )
    return render_template('main/reports.html', **context)

@main_bp.route("/expenses/form/", methods=["POST", "GET"])
@require_login
@admin_required
def expenses_form():
    form = ExpensesForm()
    if form.validate_on_submit():
        amount = form.amount.data
        op_expenses = form.op_expenses.data
        expenses = Expenses(amount=amount, operating_expenses=op_expenses)
        db.session.add(expenses)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('main/expenses_form.html', form=form)

@main_bp.route("/capital/form/", methods=["POST", "GET"])
@require_login
@admin_required
def capital_form():
    form = CapitalForm()
    if form.validate_on_submit():
        amount = form.amount.data
        capital = Capital(amount=amount)
        db.session.add(capital)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('main/add_capital.html', form=form)

@main_bp.route("/send_report/", methods=["POST", "GET"])
@require_login
def send_report():
    form = ReportForm()
    if form.validate_on_submit():
        subject = form.subject.data
        message = form.message.data
        report = Report(subject=subject, message=message, user=load_user())
        db.session.add(report)
        db.session.commit()
        return redirect(url_for('main.profile'))
    return render_template('main/report_form.html', form=form)