import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import desc

db = SQLAlchemy()


class SecretQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    def __str__(self):
        return self.question


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column(db.String(120), nullable=False)
    created_on = db.Column(db.DateTime(timezone=True),
                            server_default=db.func.now())
    last_modified = db.Column(db.DateTime(
        timezone=True), nullable=False, server_default=db.func.now())
    last_login = db.Column(db.DateTime(timezone=True))
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(255), unique=True)
    is_email_verified = db.Column(db.Boolean, default=False)

    # relationships
    secret_question_id = db.Column(db.Integer, db.ForeignKey(
        "secret_question.id", ondelete="CASCADE"))
    secret_question = db.relationship("SecretQuestion", backref=db.backref("user", uselist=False, cascade="all, delete",
                                                                        passive_deletes=True))


    user_details_id = db.Column(db.Integer, db.ForeignKey(
        "user_details.id", ondelete="CASCADE"))
    user_details = db.relationship("UserDetails", backref=db.backref("user", uselist=False, cascade="all, delete",
                                                                        passive_deletes=True))


    def __str__(self):
        return f"@{self.username}"

    def hide_email(self):
        first = self.email[0]
        at_sign = self.email.find('@')
        last = self.email[at_sign - 1]
        domain = self.email[at_sign + 1:]
        return first + (at_sign - 2) * '*' + last + '@' + domain


    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def recent_payment(self):
        return Payment.query.join(User.payments).order_by(db.desc(Payment.date_paid)).filter(Payment.user_id == self.id).first()

    @property
    def current_payment(self):
        return Payment.query.order_by(db.asc(Payment.due_date)).filter(Payment.user_id == self.id).filter(
            Payment.is_expired == False).first()

    @property
    def due_date(self):
        return self.current_payment.due_date or None


class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(11))
    social_media = db.Column(db.String(255))
    about = db.Column(db.String(255))

    def __str__(self) -> str:
        middle_name = f"{self.middle_name} " if self.middle_name else ""
        return f"{self.first_name} {middle_name}{self.last_name}".title()


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f"{self.price} - {self.speed} mbps"

    def __repr__(self) -> str:
        return f"{self.price} - {self.speed} mbps"


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.String(80))
    date_paid = db.Column(db.DateTime(timezone=True),
                          default=datetime.datetime.now())
    due_date = db.Column(db.DateTime(timezone=True), nullable=False,
                         default=datetime.datetime.now() + datetime.timedelta(days=30))
    receipt = db.Column(db.String(255), unique=True)
    receipt_id = db.Column(db.Integer, unique=True)
    amount = db.Column(db.Float, nullable=False)

    # relationships
    received_by_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False)
    received_by = db.relationship("User", foreign_keys=[received_by_id])

    plan_id = db.Column(db.Integer, db.ForeignKey(
        "plan.id", ondelete="CASCADE"))
    plan = db.relationship("Plan", backref='payment')

    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref=db.backref("payments", cascade="all, delete", passive_deletes=True),
                            foreign_keys=[user_id])

    def __str__(self) -> str:
        return str(self.plan)

    @hybrid_property
    def is_expired(self):
        return self.due_date < datetime.datetime.now()


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    created_on = db.Column(db.DateTime(timezone=True),
                            server_default=db.func.now())
    receipt = db.Column(db.String(255), unique=True)
    receipt_id = db.Column(db.Integer, unique=True)

    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref=db.backref("expenses", cascade="all, delete", passive_deletes=True),
                            foreign_keys=[user_id])


    def __str__(self) -> str:
        return self.name