from datetime import datetime
from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_session import Session

# Extensions
from app.models import db
from app.extensions.cloud_image import CloudImage
from .extensions.flask_captcha import FlaskCaptcha
from flask_migrate import Migrate
from flask_talisman import Talisman


captcha = FlaskCaptcha()
cloud_image = CloudImage()
talisman = Talisman()


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    # Blueprints
    blueprints(app)

    # Context Processor
    context_processor(app)

    extensions(app)

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

    # API
    from app.api import api_bp

    app.register_blueprint(api_bp)


# Extensions initialize
def extensions(app: Flask):
    db.init_app(app)
    db.app = app

    Session(app)
    captcha.init_app(app)

    cloud_image.init_app(app)

    Migrate(app, db)

    talisman.init_app(
        app,
        content_security_policy=app.config.get('CSP')
    )


# Context Processor
def context_processor(app: Flask):
    from app.auth.utils import load_user

    app.jinja_env.globals["load_user"] = load_user

    from app.utils import time_ago

    app.jinja_env.globals["time_ago"] = time_ago

    from app.utils import loads_token, dumps_token

    app.jinja_env.globals["loads_token"] = loads_token
    app.jinja_env.globals["dumps_token"] = dumps_token
