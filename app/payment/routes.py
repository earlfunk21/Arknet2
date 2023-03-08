import datetime
from app.models import Payment, User, db
from app.payment import payment_bp
from app.payment.forms import PaymentForm
from flask import render_template, abort, request, redirect, url_for, flash
from app.auth.utils import admin_required, load_user, require_login
from sqlalchemy import or_
from app.utils import loads_token
from app import fik


@payment_bp.route("/form/", methods=["POST", "GET"])
@require_login
@admin_required
def payment_form():
    form = PaymentForm()
    if form.validate_on_submit():
        remarks = form.remarks.data
        plan = form.plan.data
        due_date = form.due_date.data
        date_paid = form.date_paid.data
        user = form.user.data
        total = form.total.data
        file = form.receipt.data
        payment = Payment(remarks=remarks,
                            due_date=due_date,
                            date_paid=date_paid,
                            plan=plan,
                            user=user,
                            received_by=load_user(),
                            amount=total)
        response = None
        if file:
            response = fik.upload(file)
            if not response:
                return abort(500)
            payment.receipt = response['url']
            payment.receipt_id = response['fileId']
        db.session.add(payment)
        db.session.commit()
        flash("Successfully Added!", 'success')
        return redirect(url_for('admin.payment.payment_table'))
    return render_template('payment/form.html', form=form)


@payment_bp.route("/")
@payment_bp.route("/page/<int:page>")
@require_login
@admin_required
def payment_table(page=1):
    token = request.args.get('token')
    file = "payment/table.html"
    payments = Payment.query.order_by(Payment.date_paid.desc())
    if token:
        try:
            search = loads_token(token, salt='search_username')
            payments = payments.join(Payment.user).filter(or_(User.username.like(f"%{search}%")))
            file = "payment/my_table.html"
        except:
            return abort(403)
    context = dict(
        payments=payments.paginate(page=page, error_out=False, per_page=10)
    )
    return render_template(file, **context)


@payment_bp.route("/edit/<token>/", methods=["POST", "GET"])
@require_login
@admin_required
def payment_edit(token):
    form = PaymentForm()
    try:
        payment_id = loads_token(token, salt='edit_payment')
    except:
        return abort(403)
    payment: Payment = Payment.query.get_or_404(payment_id)
    if form.validate_on_submit():
        remarks = form.remarks.data
        plan = form.plan.data
        date = form.date.data
        user = form.user.data
        total = form.total.data
        payment.remarks = remarks
        payment.due_date = date
        payment.plan = plan
        payment.user = user
        payment.amount=total
        db.session.commit()
        flash("Successfully Edited!", 'success')
        return redirect(url_for('admin.payment.payment_table'))
    form.plan.default = payment.plan
    form.user.default = payment.user
    form.total.default = payment.amount
    form.date.default = payment.due_date
    form.remarks.default = payment.remarks
    form.process()
    return render_template('payment/edit.html', form=form, payment_id=payment_id)


@payment_bp.route("/delete/<token>/")
def delete_payment(token):
    try:
        payment_id = loads_token(token, salt='delete_payment')
    except:
        return abort(403)
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    flash('Successfully Deleted!', 'success')
    return redirect(url_for('admin.payment.payment_table'))