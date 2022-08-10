import datetime
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import extract

db = SQLAlchemy()


class SecretQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False, unique=True)

    def __str__(self):
        return self.question


class SecretAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(255), nullable=False)
    secret_question_id = db.Column(db.Integer, db.ForeignKey("secret_question.id"), nullable=False)
    secret_question = db.relationship("SecretQuestion")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column(db.String(120), nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    last_modified = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    last_login = db.Column(db.DateTime(timezone=True))
    is_admin = db.Column(db.Boolean, default=False)

    # relationships
    secret_answer_id = db.Column(db.Integer, db.ForeignKey("secret_answer.id", ondelete="CASCADE"), nullable=False)
    secret_answer = db.relationship("SecretAnswer", backref=db.backref("user", uselist=False, cascade="all, delete",
                                                                       passive_deletes=True))

    user_details_id = db.Column(db.Integer, db.ForeignKey("user_details.id", ondelete="CASCADE"), nullable=False)
    user_details = db.relationship("UserDetails", backref=db.backref("user", uselist=False, cascade="all, delete",
                                                                     passive_deletes=True))

    def __str__(self):
        return f"@{self.username}"

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
        return Payment.query.join(User.payments).order_by(Payment.date_paid.desc()).first()

    @property
    def current_payment(self):
        return Payment.query.order_by(Payment.due_date.asc()).filter(Payment.user_id==self.id).filter(Payment.is_expired == False).first()

    @hybrid_property
    def is_active(self):
        return User.query.join(Payment, Payment.is_expired == False).first()

    @is_active.expression
    def is_active(cls):
        return Payment.is_expired == False
    
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
    about = db.Column(db.String(255))

    # relationships
    social_media_id = db.Column(db.Integer, db.ForeignKey("social_media.id", ondelete="CASCADE"), nullable=False)
    social_media = db.relationship("SocialMedia",
                                   backref=db.backref("user_details", uselist=False, cascade="all, delete",
                                                      passive_deletes=True))

    def __str__(self) -> str:
        middle_name = f"{self.middle_name} " if self.middle_name else ""
        return f"{self.first_name} {middle_name}{self.last_name}".title()


class SocialMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(255))
    account_name = db.Column(db.String(255))

    def __str__(self) -> str:
        return self.company


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f"{self.price} - {self.speed} mbps"
    
    @classmethod
    def plan_data(cls):
        return db.session.query(Plan, db.func.count(Payment.id)).join(Plan).group_by(Plan.id).all()


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.String(80))
    date_paid = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    due_date = db.Column(db.DateTime(timezone=True), nullable=False,
                         default=datetime.datetime.now() + datetime.timedelta(days=30))

    # relationships
    received_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    received_by = db.relationship("User", foreign_keys=[received_by_id])

    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id", ondelete="CASCADE"))
    plan = db.relationship("Plan", backref='payment')

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref=db.backref("payments", cascade="all, delete", passive_deletes=True),
                           foreign_keys=[user_id])
    
    def __str__(self) -> str:
        return str(self.plan)

    @hybrid_property
    def is_expired(self):
        return self.due_date < datetime.datetime.now()
    
    @classmethod
    def sales_data(cls):
        return db.session.query(Payment,
                         db.func.sum(Plan.price)).\
                             join(Plan).\
                                 group_by(extract('month', Payment.date_paid),
                                          extract('year', Payment.date_paid)).\
                                     order_by(Payment.date_paid).all()
    
    @classmethod
    def total_sales(cls):
        return db.session.query(db.func.sum(Plan.price)).join(Payment).first()[0] or 0

        
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(80), nullable=False)
    date_reported = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now())

    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref=db.backref("reports", cascade="all, delete", passive_deletes=True))

    def __str__(self) -> str:
        return self.subject[:5]


class OperatingExpenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    operating_expenses_id = db.Column(db.Integer, db.ForeignKey("operating_expenses.id", ondelete="CASCADE"))
    operating_expenses = db.relationship("OperatingExpenses", backref='expenses')
    date_reported = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now())

    @classmethod
    def total_expenses(self):
        return db.session.query(db.func.sum(Expenses.amount)).first()[0] or 0
    
    @classmethod
    def expenses_data(self):
        return db.session.query(OperatingExpenses.name,
                         db.func.sum(Expenses.amount)).\
                             join(Expenses).\
                                 group_by(OperatingExpenses).\
                                     order_by(db.func.sum(Expenses.amount)).all()
    
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now())
    
    @classmethod
    def total_budget(self):
        return db.session.query(db.func.sum(Budget.amount)).first()[0] or 0
