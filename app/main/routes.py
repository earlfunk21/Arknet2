import datetime
from flask import abort, render_template, request, redirect, url_for, flash, jsonify
from itsdangerous import BadSignature
from app.auth.utils import admin_required, load_user, require_login
from app.models import Payment, Plan, User
from app.main import main_bp

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
    total_users = len(User.query.filter(User.is_admin==False).all())

    # Total active users
    active_users = len(
        User.query.join(User.payments).filter(Payment.is_expired == False).filter(Payment.user_id == User.id).filter(User.is_admin==False).all()
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
    users = db.session.query(User).filter(User.is_admin == False).all()

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
        social_media = request.form["social_media"]
        user.user_details.about = about
        user.user_details.phone = phone
        user.user_details.social_media = social_media
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
    return jsonify(plans_lists)


@main_bp.route("/reports/", defaults={"page": 1})
@main_bp.route("/user_is_admin/<int:user_id>/<int:is_admin>/")
@require_login
@admin_required
def is_admin(user_id, is_admin):
    user = User.query.get(user_id)
    user.is_admin = bool(is_admin)
    db.session.commit()
    if bool(is_admin):
        flash(f"@{user.username} is now admin", "success")
    else:
        flash(f"@{user.username} is now user", "success")
    return redirect(url_for("main.dashboard"))
