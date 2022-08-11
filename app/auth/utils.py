
from os import abort
from flask import redirect, request, session, url_for
from app.models import db, User
from app.auth import auth_bp


__all__ = ('authenticate', "login_user", "logout_user", "require_login", "load_user", "already_login")


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    
def already_login(func):
    def decors(*args, **kwargs):
        if load_user():
            return "You are already Login"
        return func(*args, **kwargs)
    decors.__name__ = func.__name__
    return decors


def login_user(user: User):
    session["username"] = user.username
    user.last_login = db.func.now()
    db.session.commit()
    

def logout_user():
    session.pop("username", None)
    
    
def require_login(func, login_url="auth.login"):
    def decors(*args, **kwargs):
        if load_user() is None:
            return redirect(url_for(login_url))
        return func(*args, **kwargs)
    decors.__name__ = func.__name__
    return decors


def admin_required(func):
    def decors(*args, **kwargs):
        if not load_user().is_admin and not request.args.get('token'):
            return abort(403)
        return func(*args, **kwargs)
    decors.__name__ = func.__name__
    return decors


def load_user() -> User:
    return User.query.filter_by(username=session.get("username")).first()
