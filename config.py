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

    SESSION_TYPE = "sqlalchemy"

    FIK_PRIVATE_KEY = os.environ.get("FIK_PRIVATE_KEY")
    FIK_PUBLIC_KEY = os.environ.get("FIK_PUBLIC_KEY")
    FIK_URL_ENDPOINT = os.environ.get("FIK_URL_ENDPOINT")

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

    CSP = {"default-src": "'self'"}


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
