
from app.admin import admin_bp
from app.models import (
    db,
    Expenses,
)


@admin_bp.cli.command("add-expenses")
def add_expenses():
    expenses = Expenses(name="Test", cost=5000, user_id=1)
    db.session.add(expenses)
    db.session.commit()