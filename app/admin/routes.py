
from app.admin import admin_bp
from app.models import (
    db,
    Expenses,
    User
)

import click


@admin_bp.cli.command("add-expenses")
def add_expenses():
    expenses = Expenses(name="Test", cost=5000, user_id=1)
    db.session.add(expenses)
    db.session.commit()


@admin_bp.cli.command("remove-user")
@click.argument("username")
def remove_user(username):
    user = User.query.filter(User.username == username).first()
    if not user:
        print("username not found. Please try again")
        return
    db.session.delete(user.user_details)
    db.session.delete(user)
    db.session.commit()
    print("Successfully removed")

@admin_bp.cli.command("add-email")
@click.argument("username", nargs=1)
@click.argument("email", nargs=1)
def add_email(username, email):
    user = User.query.filter(User.username == username).first()
    if not user:
        print("username not found. Please try again")
        return
    user.email = email
    user.is_email_verified = True
    db.session.commit()
    print("Successfully Added email")

@admin_bp.cli.command("remove-email")
@click.argument("username")
def remove_email(username):
    user = User.query.filter(User.username == username).first()
    if not user:
        print("username not found. Please try again")
        return
    user.is_email_verified = False
    db.session.commit()
    print("Successfully removed email")

