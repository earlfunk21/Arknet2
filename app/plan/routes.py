from app.models import Plan, db
from app.plan import plan_bp
from flask import render_template, redirect, url_for, flash, abort, jsonify, request

from app.plan.forms import CreatePlanForm
from app.utils import loads_token


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
        flash('Successfully Created', 'success')
        return redirect(url_for('admin.plan.plan_lists'))
    return render_template("plan/form.html", form=form)


@plan_bp.route("/edit/<token>/", methods=["POST", "GET"])
def plan_edit(token):
    form = CreatePlanForm()
    try:
        plan_id = loads_token(token, salt='edit_plan')
    except:
        return abort(403)
    plan = Plan.query.get_or_404(plan_id)
    form.price.data = plan.price
    form.speed.data = plan.speed
    if form.validate_on_submit():
        speed = request.form.get('speed')
        price = request.form.get('price')
        plan_id = request.form.get('plan_id')
        plan = Plan.query.get_or_404(plan_id)
        plan.price = price
        plan.speed = speed
        db.session.commit()
        flash('Successfully Created', 'success')
        return redirect(url_for('admin.plan.plan_lists'))
    return render_template("plan/edit.html", form=form, plan_id=plan.id)


@plan_bp.route("/delete/<token>")
def delete_plan(token):
    try:
        plan_id = loads_token(token, salt='delete_plan')
    except:
        return abort(403)
    plan = Plan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    flash('Successfully Deleted!', 'success')
    return redirect(url_for('admin.plan.plan_lists'))
    