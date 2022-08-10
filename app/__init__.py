from flask import Flask
from config import DevelopmentConfig, ProductionConfig


# Extensions
from app.models import db
from flask_migrate import Migrate
from flask_sessionstore import Session
from flask_session_captcha import FlaskSessionCaptcha


migrate = Migrate()

sess = Session()
captcha = FlaskSessionCaptcha()

# Creating Application
def create_app(config=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Extensions
    extensions(app)
    
    # Blueprints
    blueprints(app)
    
    context_processor(app)
    
    return app


# Registered Blueprints
def blueprints(app: Flask):
    
    # Authentication
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Admin
    from app.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from app.main import main_bp
    app.register_blueprint(main_bp)
    

# Extensions initialize
def extensions(app: Flask):
    db.init_app(app)
    db.app = app
    
    migrate.init_app(app, db)
    migrate.app = app
    
    sess.init_app(app)
    
    captcha.init_app(app)
    

def context_processor(app: Flask):
    
    from app.auth.utils import load_user
    
    app.jinja_env.globals['load_user'] = load_user
    
    from app.utils import time_ago
    app.jinja_env.globals['time_ago'] = time_ago
    
    from app.utils import loads_token, dumps_token
    app.jinja_env.globals['loads_token'] = loads_token
    app.jinja_env.globals['dumps_token'] = dumps_token