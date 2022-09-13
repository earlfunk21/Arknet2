import base64
import os
import random
from flask import session, Flask, jsonify, Markup, url_for, abort
from captcha.image import ImageCaptcha


class FlaskCaptcha(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.captcha_enabled = app.config.get('FLASK_CAPTCHA_ENABLED', True)
        self.captcha_key = app.config.get("FLASK_CAPTCHA_KEY")
        self.length = app.config.get("FLASK_CAPTCHA_LENGTH")
        self.size = {}
        self.size["height"] = app.config.get("FLASK_CAPTCHA_HEIGHT")
        self.size["width"] = app.config.get("FLASK_CAPTCHA_WIDTH")
        app.session_interface.db.create_all()
        self.image = ImageCaptcha(**self.size)
        self.answer = str(random.randrange(10**self.length)).zfill(self.length)

        app.jinja_env.globals["captcha"] = self.captcha_html

        @app.route("/generate_captcha/")
        def generate_captcha():
            return jsonify(data=self.generate())

    def generate(self):
        answer = str(random.randrange(10**self.length)).zfill(self.length)
        image_data = self.image.generate(answer)
        base64_captcha = base64.b64encode(image_data.getvalue()).decode("ascii")
        session[self.captcha_key] = answer
        return base64_captcha

    def validate(self, answer):
        if not self.captcha_enabled:
            return True 
        return session[self.captcha_key] == answer

    def captcha_html(self):
        if not self.captcha_enabled:
            return ''
        return Markup(
            """
                <div class="row">
                    <div class="col-12 mb-3">
                      <img src="" alt="captcha" id="captcha">
                    </div>
                    <div class="col-12 mx-2">
                      <a onclick="setCaptcha();" class="btn border-0 btn-success">Refresh</a>
                    </div>
                  </div>
                  <script>
                    function setCaptcha(){
                      $.getJSON('%s', function(data){
                        $('#captcha').attr('src', 'data:image/png;base64, ' + data.data)
                      })
                    }
                    setCaptcha()
                </script>
            """
            % (
                url_for(
                    "generate_captcha",
                )
            )
        )
