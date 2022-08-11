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
    CAPTCHA_ENABLE = True
    CAPTCHA_LENGTH = 5
    CAPTCHA_SESSION_KEY = 'captcha_image'
    SESSION_TYPE = 'sqlalchemy'
    FIK_PRIVATE_KEY=os.getenv("FIK_PRIVATE_KEY")
    FIK_PUBLIC_KEY=os.getenv("FIK_PUBLIC_KEY")
    FIK_URL_ENDPOINT=os.getenv("FIK_URL_ENDPOINT")
    

class DevelopmentConfig(Config):
    DEBUG = True
    
    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, 'dev-data.db')

# create the production config
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    