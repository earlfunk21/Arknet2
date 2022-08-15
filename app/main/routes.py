import datetime
from flask import abort, render_template, request, redirect, url_for, flash, jsonify
from itsdangerous import BadSignature
from app.auth.utils import admin_required, load_user, require_login
from app.main.form import ReportForm
from app.models import Payment, Plan, Report, User
from app.main import main_bp
from sqlalchemy import and_

from app.utils import extract_date, loads_token
from app.models import db


@main_bp.route("/dashboard/")
@require_login
@admin_required
def dashboard():

    # Users created on by months
    user_create_on = (
        db.session.query(User.created_on, db.func.count(User.created_on))
        .group_by(*extract_date(User.created_on, "Month"))
        .all()
    )

    # Total Users
    total_users = len(User.query.all())

    # Total active users
    active_users = len(
        User.query.join(User.payments).filter(User.is_active == True).all()
    )

    # Total Gross Sales
    total_gross_sales = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(
            *extract_date(
                Payment.date_paid, filter_date=request.args.get(
                    "filter", "Month")
            )
        )
        .first()[0]
    )

    # Gross sales by months for graph
    gross_sales = (
        db.session.query(Payment.date_paid, db.func.sum(Payment.amount))
        .group_by(*extract_date(Payment.date_paid, "Month"))
        .all()
    )

    # Plan Data for graph
    plan_data = (
        db.session.query(Plan, db.func.count(Payment.id))
        .join(Plan)
        .group_by(Plan.id)
        .all()
    )

    # Lists of Payments
    payments = Payment.query.order_by(
        Payment.date_paid.desc()
        ).limit(5).all()

    # Lists of Users
    users = User.query.join(User.payments).filter(User.is_active == True).all()

    # Lists of Reports
    reports = Report.query.order_by(Report.date_reported.desc()).limit(5).all()

    # Context
    context = dict(
        user_created_on=user_create_on,
        total_users=total_users,
        active_users=active_users,
        total_gross_sales=total_gross_sales or 0,
        gross_sales=gross_sales,
        plan_data=plan_data,
        payments=payments,
        users=users,
        reports=reports,
    )

    return render_template("main/dashboard.html", **context)


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
        about = request.form["about"]
        phone = request.form["phone"]
        company = request.form["company"]
        account_name = request.form["account_name"]
        user.user_details.about = about
        user.user_details.phone = phone
        user.user_details.social_media.name = company
        user.user_details.social_media.account_name = account_name
        db.session.commit()
        flash("Successfully Edited", "success")
        return redirect(request.url)
    return render_template("main/profile.html", user=user)


@main_bp.route("/plans/")
def all_plans():
    plans = Plan.query.all()
    plans_lists = []
    for plan in plans:
        plans_lists.append(
            dict(id=plan.id, price=plan.price, speed=plan.speed, days=plan.days)
        )
    return jsonify(*plans_lists)


@main_bp.route("/reports/", defaults={"page": 1})
@main_bp.route("/reports/<int:page>/")
@require_login
@admin_required
def report_lists(page):
    reports = Report.query.order_by(Report.date_reported.desc()).paginate(
        page=page, error_out=False, per_page=10
    )
    context = dict(reports=reports)
    return render_template("main/reports.html", **context)


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
        flash("Successfully Reported!", "success")
        return redirect(url_for("main.profile"))
    return render_template("main/report_form.html", form=form)
