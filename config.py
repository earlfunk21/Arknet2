import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__name__))

load_dotenv(os.path.join(basedir, ".env"))


# Create the super class
class Config(object):
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_KEY = os.environ.get("ADMIN_KEY")
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/tmp/flask_session'
    SESSION_FILE_THRESHOLD = 1000
    CLOUD_NAME = os.environ.get("CLOUD_NAME")
    API_KEY = os.environ.get("API_KEY")
    API_SECRET = os.environ.get("API_SECRET")


    FLASK_CAPTCHA_LENGTH = 5
    FLASK_CAPTCHA_KEY = os.environ.get("FLASK_CAPTCHA_KEY")
    FLASK_CAPTCHA_HEIGHT = 90
    FLASK_CAPTCHA_WIDTH = 280

    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")


class DevelopmentConfig(Config):
    DEBUG = True

    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "dev-data.db")

    FLASK_CAPTCHA_ENABLED = False

    SSL_DISABLE = True

    CSP = {
        # Fonts from fonts.google.com
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "font-src": ["'self'", "fonts.gstatic.com"],
        "style-src": ["'self'", "fonts.googleapis.com", "'unsafe-inline'"],
        "img-src": ["*", "'self'", "data:", "https:"],
    }


# create the production config
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data.db")

    CSP = {
        # Fonts from fonts.google.com
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "font-src": ["'self'", "fonts.gstatic.com"],
        "style-src": ["'self'", "fonts.googleapis.com", "'unsafe-inline'"],
        "img-src": ["*", "'self'", "data:", "https:"],
    }
