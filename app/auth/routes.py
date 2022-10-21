
from flask import abort, flash, redirect, render_template, url_for, request
from itsdangerous import BadSignature, SignatureExpired
from app.auth import auth_bp
from app.auth.forms import UserDetailsForm, ForgotPasswordForm, LoginForm, RegistrationForm, UpdatePasswordForm
from app.auth.utils import *
from app.models import SecretQuestion, db, UserDetails, User
from app.utils import dumps_token, loads_token


@auth_bp.route("/login/", methods=["GET", "POST"])
@already_login
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = authenticate(username, password)
        if user:
            login_user(user)
            flash("Successfully Login", "success")
            return redirect(url_for('main.profile'))
        form.password.errors.append("Password is incorrect")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout/", methods=["GET"])
@require_login
def logout():
    logout_user()
    flash("Successfully Logout", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/", methods=["GET", "POST"])
@already_login
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        question = form.question.data
        answer = form.answer.data
        user = {'username': username, 'password': password, 'question': question, 'answer': answer}
        token = dumps_token(user, salt="register")
        return redirect(url_for("auth.register_about", token=token))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/register/about/<token>/", methods=["GET", "POST"])
def register_about(token):
    try:
        token = loads_token(token, max_age=1800, salt="register")
    except SignatureExpired:
        return abort(401)
    except BadSignature:
        return abort(401)
    form = UserDetailsForm()
    if form.validate_on_submit():
        first_name = form.first_name.data.capitalize()
        middle_name = form.middle_name.data.capitalize()
        last_name = form.last_name.data.capitalize()
        address = form.address.data.title()
        phone = form.phone.data
        social_media = form.social_media.data
        user_details = UserDetails(first_name=first_name,
                                middle_name=middle_name,
                                last_name=last_name,
                                address=address,
                                phone=phone,
                                social_media=social_media)
        secret_question = SecretQuestion(answer=token['answer'], question=token['question'])
        user = User(username=token['username'],
                    password=token['password'],
                    secret_question=secret_question,
                    user_details=user_details)
        db.session.add(user)
        db.session.commit()
        flash("Successfully Created!", 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_about.html', form=form)


@auth_bp.route("/forgot_password/", methods=["GET", "POST"])
@already_login
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        username = form.username.data
        token = dumps_token(username, salt="forgot_password")
        return redirect(url_for('auth.update_password', token=token))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/update_password/", defaults={"token": None}, methods=["GET", "POST"])
@auth_bp.route("/update_password/<token>", methods=["GET", "POST"])
def update_password(token):
    user = load_user()
    if token:
        username = loads_token(token, max_age=1800, salt="forgot_password")
        user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for("auth.forgot_password"))
    form = UpdatePasswordForm(user)
    if form.validate_on_submit():
        password = form.password.data
        user.password = password
        user.last_modified = db.func.now()
        db.session.commit()
        flash("Password updated successfully", "success")
        return redirect(url_for('auth.logout'))
    return render_template("auth/update_password.html", form=form, question=user.secret_question.question)
