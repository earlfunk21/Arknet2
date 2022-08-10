import datetime
from app.models import Payment, db
from app.payment import payment_bp
from app.payment.forms import PaymentForm
from flask import render_template
from app.auth.utils import admin_required, load_user, require_login


@payment_bp.route("/form/", methods=["POST", "GET"])
@require_login
@admin_required
def payment_form():
    form = PaymentForm()
    if form.validate_on_submit():
        remarks = form.remarks.data
        plan = form.plan.data
        days = form.days.data
        months = form.months.data * 30
        years = form.years.data * 365
        user = form.user.data
        due_date = datetime.datetime.now() + datetime.timedelta(days=days + months + years)
        if user.recent_payment:
            due_date = user.recent_payment.due_date + datetime.timedelta(days=days + months + years)
        payment = Payment(remarks=remarks, due_date=due_date, plan=plan, user=user, received_by=load_user())
        db.session.add(payment)
        db.session.commit()
        return "Submitted"
    return render_template('payment/form.html', form=form)

@payment_bp.route("/")
@payment_bp.route("/page/<int:page>")
@require_login
@admin_required
def payment_table(page=1):
    payments = Payment.query.order_by(Payment.date_paid.desc()).paginate(page=page, error_out=False, per_page=10)
    context = dict(
        payments=payments
    )
    return render_template("payment/table.html", **context)

