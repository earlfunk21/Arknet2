from flask import Blueprint, request


api_bp = Blueprint("api_bp", __name__, url_prefix="/api")

@api_bp.before_request
def api_request():
    from app.auth.utils import authenticate

    auth = request.authorization
    user = authenticate(auth.username, auth.password)
    if not (user and user.is_admin):
        return ('Unauthorized', 401, {
            'WWW-Authenticate': 'Basic realm="Login Required"'
        })


from app.api import routes