import cloudinary
from cloudinary.uploader import upload as ci_upload
from cloudinary.utils import cloudinary_url
from flask import Flask
from werkzeug.utils import secure_filename


class CloudImage(object):
    imagekit: cloudinary

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        cloud_name = app.config.get("CLOUD_NAME")
        api_key = app.config.get("API_KEY")
        api_secret = app.config.get("API_SECRET")
        self.imagekit = cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
            unique_filename = True,
        )

    def upload(self, file):
        return ci_upload(file)

    def get_url(self, id, **kwargs):
        return cloudinary.CloudinaryImage(id).build_url(**kwargs)
