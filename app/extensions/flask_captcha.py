import base64
import random
from uuid import uuid4
from flask import session, Flask, jsonify, url_for, abort
from captcha.image import ImageCaptcha
from itsdangerous import URLSafeTimedSerializer


class FlaskCaptcha(object):
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        
        self.captcha_key = app.config.get('FLASK_CAPTCHA_KEY')
        self.length = app.config.get('FLASK_CAPTCHA_LENGTH')
        self.size = {}
        self.size['height'] = app.config.get('FLASK_CAPTCHA_HEIGHT')
        self.size['width'] = app.config.get('FLASK_CAPTCHA_WIDTH')
        self.usts = URLSafeTimedSerializer(self.captcha_key)
        app.session_interface.db.create_all()
        
        @app.route('/generate_captcha/')
        def generate_captcha():
            return jsonify(data=self.generate())
        
    def generate(self):
        image = ImageCaptcha(**self.size)
        answer = str(random.randrange(10**self.length)).zfill(self.length)
        image_data = image.generate(answer)
        base64_captcha = base64.b64encode(image_data.getvalue()).decode("ascii")
        session[self.captcha_key] = answer
        return base64_captcha
    
    def validate(self, answer):
        print(session[self.captcha_key])
        return session[self.captcha_key] == answer