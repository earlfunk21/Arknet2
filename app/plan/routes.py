from app.models import Plan, db
from app.plan import plan_bp
from flask import render_template, redirect, url_for

from app.plan.forms import CreatePlanForm


@plan_bp.route("/")
def plan_lists():
    plans = db.session.query(Plan).order_by(Plan.price).all()
    context = dict(
        plans=plans
    )
    return render_template('plan/lists.html', **context)


@plan_bp.route("/form/", methods=["POST", "GET"])
def plan_form():
    form = CreatePlanForm()
    if form.validate_on_submit():
        speed = form.speed.data
        price = form.price.data
        plan = Plan(speed=speed, price=price)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for('admin.plan.plan_lists'))
    return render_template("plan/form.html", form=form)