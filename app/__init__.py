from datetime import datetime
from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_session import Session

# Extensions
from app.models import Expenses, User, UserDetails, db
from app.extensions.imagekit import FlaskImageKit
from .extensions.flask_captcha import FlaskCaptcha
from flask_migrate import Migrate

from openpyxl import load_workbook


captcha = FlaskCaptcha()
fik = FlaskImageKit()


def create_app(config=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    # Extensions
    extensions(app)

    # Blueprints
    blueprints(app)

    # Context Processor
    context_processor(app)


    # Initialization
    with app.app_context():
        @app.cli.command("init-arknet")
        def init_arknet():
            db.create_all()
    
            users = []
        
            admin = User(
                username=app.config.get("ADMIN_USERNAME"),
                password=app.config.get("ADMIN_PASSWORD"),
                is_admin=True,
            )
            users.append(admin)
        
            # Load Users
            workbook = load_workbook("Arknet.xlsx")
            sheet = workbook.active
            for last_name, first_name in sheet['K3': 'L34']:
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
                date = str(date.value).replace('Released ', '')
                date = datetime.strptime(date, '%m/%d/%Y')
        
                expenses = Expenses(
                    name=name.value,
                    cost = float(amount.value),
                    created_on=date,
                    user=admin
                )
                expenseses.append(expenses)
        
            db.session.add_all(expenseses)
            db.session.commit()
        
            print("Successfully initialized")

    return app


# Registered Blueprints
def blueprints(app: Flask):
    # Authentication
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Admin
    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Main
    from app.main import main_bp
    app.register_blueprint(main_bp)


# Extensions initialize
def extensions(app: Flask):
    db.init_app(app)
    db.app = app

    Session(app)
    captcha.init_app(app)

    fik.init_app(app)

    Migrate(app, db)


# Context Processor
def context_processor(app: Flask):
    from app.auth.utils import load_user
    app.jinja_env.globals['load_user'] = load_user

    from app.utils import time_ago
    app.jinja_env.globals['time_ago'] = time_ago

    from app.utils import loads_token, dumps_token
    app.jinja_env.globals['loads_token'] = loads_token
    app.jinja_env.globals['dumps_token'] = dumps_token
