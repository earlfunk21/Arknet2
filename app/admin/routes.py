import datetime
from flask import current_app
from app.admin import admin_bp
from app.models import Payment, Plan, Report, SocialMedia, UserDetails, db, SecretQuestion, SecretAnswer, User
import click

from ..utils import extract_date


@admin_bp.cli.command("create-all")
def create_all():
    db.create_all()
    
@admin_bp.cli.command("drop-all")
def drop_all():
    db.drop_all()

@admin_bp.cli.command("init")
def init():
    db.create_all()
    question1 = SecretQuestion(question="What was your first car?")
    question2 = SecretQuestion(question="What elementary school did you attend?")
    question3 = SecretQuestion(question="What is your mother's maiden name?")
    question4 = SecretQuestion(question="What is the name of your first pet?")
    question5 = SecretQuestion(question="What is the name of the town where you were born?")
    db.session.add_all([question1, question2, question3, question4, question5])
    
    secret_question = SecretQuestion.query.get(current_app.config.get("SECRET_QUESTION_ID"))
    secret_answer = SecretAnswer(answer=current_app.config.get("SECRET_ANSWER"), secret_question=secret_question)
    
    plan1 = Plan(price=1500, speed=50, days=30)
    plan2 = Plan(price=2500, speed=100, days=30)
    plan3 = Plan(price=500, speed=15, days=30)
    db.session.add_all([plan1, plan2, plan3])
    
    social_media = SocialMedia(name="facebook", account_name="user@test")
    
    user_details = UserDetails(first_name="admin", middle_name="admin", last_name="admin", address="secret", phone="secret", social_media=social_media)
    
    user = User(username="admin", password="admin123", secret_answer=secret_answer, is_admin=True, user_details=user_details)
    db.session.add(user)

    db.session.commit()


@admin_bp.cli.command("add-payment")
def add_payment():
    received_by = User.query.filter_by(username="admin").first()
    user = User.query.filter_by(username="moraxfunk").first()
    due_date = datetime.datetime.now() + datetime.timedelta(days=30)
    if user.recent_payment:
        due_date = user.recent_payment.due_date + datetime.timedelta(days=30)
    plan = Plan.query.get(1)
    payment = Payment(user=user, received_by=received_by, due_date=due_date, plan=plan, remarks="paid")
    db.session.add(payment)
    db.session.commit()
    

@admin_bp.cli.command("test1")
def test():
    # All inactive users
    inactive_users = User.query.join(User.payments).filter(User.is_active==False).all()
    print(inactive_users)
    
    # All active users
    active_users = User.query.join(User.payments).filter(User.is_active==True).all()
    print(active_users)
        
    print("________")
    user = User.query.get(1)
    
    print(user.current_payment)
    
    print("________")

    print(db.session.query(Payment, db.func.sum(Payment.amount)).group_by(Payment.date_paid).all())
    
    print("________")
    
    print(db.session.query(User.created_on, db.func.count(User.id)).group_by(*extract_date(User.created_on, 'Month')).all())


@admin_bp.cli.command("add-report")
def add_report():
    user = User.query.get(1)
    report = Report(user=user, subject="Matud nako", message="Yawa ka lag baya ani oy Yawa ka lag baya ani oy Yawa ka lag baya ani oy Yawa ka lag baya ani oy")
    db.session.add(report)
    db.session.commit()
