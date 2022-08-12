import os

basedir = os.path.abspath(os.path.dirname(__name__))

# Create the super class
class Config(object):
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
        # SECRET
    SECRET_QUESTION_ID = os.getenv("SECRET_QUESTION_ID")
    SECRET_ANSWER = os.getenv("SECRET_ANSWER")
    
    ADMIN_KEY = os.getenv("ADMIN_KEY")
    
    SESSION_TYPE = 'sqlalchemy'
    
    FIK_PRIVATE_KEY=os.getenv("FIK_PRIVATE_KEY")
    FIK_PUBLIC_KEY=os.getenv("FIK_PUBLIC_KEY")
    FIK_URL_ENDPOINT=os.getenv("FIK_URL_ENDPOINT")
    
    FLASK_CAPTCHA_LENGTH = 5
    FLASK_CAPTCHA_KEY = os.getenv("FLASK_CAPTCHA_KEY")
    FLASK_CAPTCHA_HEIGHT = 90
    FLASK_CAPTCHA_WIDTH = 280
    

class DevelopmentConfig(Config):
    DEBUG = True
    CAPTCHA_ENABLE = False
    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, 'dev-data.db')

# create the production config
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    CAPTCHA_ENABLE = True
    