from imagekitio import ImageKit
from flask import Flask
from werkzeug.utils import secure_filename

class FlaskImageKit(object):
    imagekit: ImageKit
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        private_key = app.config.get('FIK_PRIVATE_KEY')
        public_key = app.config.get('FIK_PUBLIC_KEY')
        url_endpoint = app.config.get('FIK_URL_ENDPOINT')
        self.imagekit = ImageKit(
            private_key=private_key,
            public_key=public_key,
            url_endpoint=url_endpoint
        )
        app.jinja_env.globals['fik_get_url'] = self.get_url
        app.jinja_env.globals['fik_get_details'] = self.get_details
        
    
    def upload(self, file):
        image = self.imagekit.upload_file(file=file,
                                          file_name=secure_filename(file.filename),
                                          options= {
                                              "is_private_file": False,
                                              "use_unique_file_name": True,
                                              })
        return image['response']
        
    def get_details(self, id):
        return self.imagekit.get_file_details(id)['response']
    
    def get_url(self, id):
        return self.get_details(id)['url']