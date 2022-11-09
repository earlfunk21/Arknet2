
from datetime import datetime
from flask import current_app
from app.admin import admin_bp
from app.models import (
    Payment,
    UserDetails,
    db,
    SecretQuestion,
    User,
    Expenses,
)

from openpyxl import load_workbook


@admin_bp.cli.command("create-all")
def create_all():
    db.create_all()


@admin_bp.cli.command("drop-all")
def drop_all():
    db.drop_all()


@admin_bp.cli.command("init")
def init():
    db.create_all()

    users = []

    admin = User(
        username=current_app.config.get("ADMIN_USERNAME"),
        password=current_app.config.get("ADMIN_PASSWORD"),
        is_admin=True,
    )
    users.append(admin)

    # Load Users
    workbook = load_workbook("Arknet.xlsx")
    sheet = workbook.active
    for first_name, last_name in sheet['K3': 'L34']:
        first_name = str(first_name.value).strip(' ').lower()
        last_name = str(last_name.value).strip(' ').lower()
        username = f"{last_name}.{first_name}"
        password = f"{last_name}123"
        user_details = UserDetails(
            first_name=first_name,
            last_name=last_name,
            address="Bougainvillea Village"
        )
        user = User(
            username=username,
            password=password,
            user_details=user_details,
            is_admin=False
        )
        users.append(user)
        
    db.session.add_all(users)

    expenseses = []
    # Load Expenses
    for date, amount, name in sheet['A10': 'C36']:
        expenses = Expenses(
            name=name.value,
            cost = int(amount.value),
            created_on=date,
            user=admin
        )
        expenseses.append(expenses)

    db.session.add_all(expenseses)
    db.session.commit()

    print("Successfully initialized")


@admin_bp.cli.command("add-expenses")
def add_expenses():
    expenses = Expenses(name="Test", cost=5000, user_id=1)
    db.session.add(expenses)
    db.session.commit()