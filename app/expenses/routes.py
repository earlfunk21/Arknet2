
from flask import request, abort, render_template, flash, redirect, url_for
from app.auth.utils import admin_required, load_user, require_login
from app.expenses import expenses_bp
from app.expenses.form import ExpensesForm
from app.models import Expenses, User, db
from app.utils import loads_token
from sqlalchemy import or_
from app import fik


@expenses_bp.route("/")
@expenses_bp.route("/page/<int:page>")
@require_login
@admin_required
def expenses_table(page=1):
    token = request.args.get('token')
    expenses = Expenses.query.order_by(Expenses.created_on.desc())
    if token:
        try:
            search = loads_token(token, salt='search_username')
            expenses = expenses.join(Expenses.user).filter(or_(User.username.like(f"%{search}%")))
        except:
            return abort(403)
    context = dict(
        expenses=expenses.paginate(page=page, error_out=False, per_page=10)
    )
    return render_template("expenses/table.html", **context)


@expenses_bp.route("/form/", methods=["POST", "GET"])
@require_login
@admin_required
def expenses_form():
    form = ExpensesForm()
    user = load_user()
    if form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        file = form.receipt.data
        expenses = Expenses(name=name, cost=cost, user=user)
        response = None
        if file:
            response = fik.upload(file)
            if not response:
                return abort(500)
            expenses.receipt = response['url']
            expenses.receipt_id = response['fileId']
        db.session.add(expenses)
        db.session.commit()
        flash("Successfully Added!", 'success')
        return redirect(url_for('admin.expenses.expenses_table'))
    return render_template('expenses/form.html', form=form)