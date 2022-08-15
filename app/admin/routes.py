import datetime
import os
from flask import current_app, Markup, render_template_string
from app.admin import admin_bp
from app.models import (
    Payment,
    Plan,
    Report,
    SocialMedia,
    UserDetails,
    db,
    SecretQuestion,
    SecretAnswer,
    User,
)


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

    db.session.add_all(
        [
            SecretQuestion(question="What was the name of your elementary / primary school?"),
            SecretQuestion(question="What is the name of the company of your first job?"),
            SecretQuestion(question="What was your favorite place to visit as a child?"),
            SecretQuestion(question="What is your spouse's mother's maiden name?"),
            SecretQuestion(question="What is the country of your ultimate dream vacation?"),
            SecretQuestion(question="What is the name of your favorite childhood teacher?"),
            SecretQuestion(question="To what city did you go on your honeymoon?"),
            SecretQuestion(question="What time of the day were you born?"),
            SecretQuestion(question="What was your dream job as a child?"),
            SecretQuestion(question="What is the street number of the house you grew up in?"),
            SecretQuestion(
                question="What is the license plate (registration) of your dad's first car?"
            ),
            SecretQuestion(question="Who was your childhood hero?"),
            SecretQuestion(question="What was the first concert you attended?"),
            SecretQuestion(question="What are the last 5 digits of your credit card?"),
            SecretQuestion(question="What are the last 5 of your Social Security number?"),
            SecretQuestion(question="What is your current car registration number?"),
            SecretQuestion(
                question="What are the last 5 digits of your driver's license number?"
            ),
            SecretQuestion(question="What month and day is your anniversary? (e.g., January 2)"),
            SecretQuestion(question="What is your grandmother's first name?"),
            SecretQuestion(question="What is your mother's middle name?"),
            SecretQuestion(
                question="What is the last name of your favorite high school teacher?"
            ),
            SecretQuestion(question="What was the make and model of your first car?"),
            SecretQuestion(question="Where did you vacation last year?"),
            SecretQuestion(question="What is the name of your grandmother's dog?"),
            SecretQuestion(question="What is the name, breed, and color of current pet?"),
            SecretQuestion(question="What is your preferred musical genre?"),
            SecretQuestion(question="In what city and country do you want to retire?"),
            SecretQuestion(
                question="What is the name of the first undergraduate college you attended?"
            ),
            SecretQuestion(question="What was your high school mascot?"),
            SecretQuestion(question="What year did you graduate from High School?"),
            SecretQuestion(question="What is the name of the first school you attended?"),
        ]
    )

    secret_question = SecretQuestion.query.get(
        current_app.config.get("SECRET_QUESTION_ID")
    )
    secret_answer = SecretAnswer(
        answer=current_app.config.get("SECRET_ANSWER"), secret_question=secret_question
    )

    social_media = SocialMedia(name="facebook", account_name="user@test")

    user_details = UserDetails(
        first_name="admin",
        middle_name="admin",
        last_name="admin",
        address="secret",
        phone="secret",
        social_media=social_media,
    )

    user = User(
        username="admin",
        password="admin123",
        secret_answer=secret_answer,
        is_admin=True,
        user_details=user_details,
    )
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
    payment = Payment(
        user=user, received_by=received_by, due_date=due_date, plan=plan, remarks="paid"
    )
    db.session.add(payment)
    db.session.commit()


@admin_bp.cli.command("test1")
def test():
    # All inactive users
    inactive_users = (
        User.query.join(User.payments).filter(User.is_active == False).all()
    )
    print(inactive_users)

    # All active users
    active_users = User.query.join(User.payments).filter(User.is_active == True).all()
    print(active_users)

    print("________")
    user = User.query.get(1)

    print(user.current_payment)

    print("________")

    print(
        db.session.query(Payment, db.func.sum(Payment.amount))
        .group_by(Payment.date_paid)
        .all()
    )

    print("________")

    print(
        db.session.query(User.created_on, db.func.count(User.id))
        .group_by(*extract_date(User.created_on, "Month"))
        .all()
    )


@admin_bp.cli.command("add-report")
def add_report():
    user = User.query.get(1)
    report = Report(
        user=user,
        subject="Matud nako",
        message="Yawa ka lag baya ani oy Yawa ka lag baya ani oy Yawa ka lag baya ani oy Yawa ka lag baya ani oy",
    )
    db.session.add(report)
    db.session.commit()


@admin_bp.cli.command("test-markup")
def test_markup():
    base_dir = os.getcwd()
    templates_dir = os.path.join(base_dir, "app", "templates")
    with open(f"{templates_dir}\\captcha.html", "r") as f:
        print(f.read())
