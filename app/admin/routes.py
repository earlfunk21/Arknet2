
from flask import current_app
from app.admin import admin_bp
from app.models import (
    Payment,
    UserDetails,
    db,
    SecretQuestion,
    User,
)


@admin_bp.cli.command("create-all")
def create_all():
    db.create_all()


@admin_bp.cli.command("drop-all")
def drop_all():
    db.drop_all()


@admin_bp.cli.command("init")
def init():
    db.create_all()

    user_details = UserDetails(
        first_name="",
        middle_name="",
        last_name="",
        address="",
        phone="",
        social_media="",
    )
    user = User(
        username=current_app.config.get("ADMIN_USERNAME"),
        password=current_app.config.get("ADMIN_PASSWORD"),
        is_admin=True,
        user_details=user_details,
    )

    db.session.add(user)
    
    db.session.commit()
