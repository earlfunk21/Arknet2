
from flask import abort, flash, redirect, render_template, url_for, request, session
from itsdangerous import BadSignature, SignatureExpired
from app.auth import auth_bp
from app.auth.forms import *
from app.auth.utils import *
from app.models import db, UserDetails, User
from app.utils import dumps_token, loads_token
from send_email import send_email


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
            return redirect(url_for("main.profile"))
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
        user = {"username": username, "password": password}
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
        user_details = UserDetails(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            address=address,
            phone=phone,
            social_media=social_media,
        )
        user = User(
            username=token["username"],
            password=token["password"],
            user_details=user_details,
        )
        db.session.add(user)
        db.session.commit()
        flash("Successfully Created!", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register_about.html", form=form)


@auth_bp.route("/forgot_password/", methods=["GET", "POST"])
@already_login
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        username = form.username.data
        token = dumps_token(username, salt="forgot_password")
        return redirect(url_for("auth.update_password", token=token))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/update_password/", defaults={"token": None}, methods=["GET", "POST"])
@auth_bp.route("/update_password/<token>", methods=["GET", "POST"])
def update_password(token):
    user = load_user()
    if token:
        try:
            data = loads_token(token, max_age=1800, salt="change_password")
            user = User.query.filter_by(username=data["username"]).first()
        except SignatureExpired:
            abort(401)
    if not user:
        return redirect(url_for("auth.forgot_password"))
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        user.password = password
        user.last_modified = db.func.now()
        db.session.commit()
        flash("Password updated successfully", "success")
        return redirect(url_for("auth.logout"))
    return render_template("auth/update_password.html", form=form)


@auth_bp.route("/change_password", methods=["POST", "GET"])
@require_login
def change_password():
    user = load_user()
    if request.method == "POST":
        data = dict(username=user.username, email=user.email)
        token = dumps_token(data, "change_password")
        link = url_for("auth.update_password", token=token, _external=True)
        html = """\
        <html>
        <body>
            <p>Click this link to change your password<br>
            <a href="{}">Change</a>
            </p>
        </body>
        </html>
        """.format(
            link
        )
        send_email(user.email, "Change Password", html)
        flash("Please check your email to change your password", category="success")
        return redirect(url_for("main.profile"))
    return render_template("auth/change_password.html")


@auth_bp.route("/verify_email/", methods=["GET", "POST"])
@require_login
def verify_email():
    user = load_user()
    form = VerifyEmailAddress()
    if form.validate_on_submit():
        email = form.email.data
        token = dumps_token(user.username, "verify_email_address")
        link = url_for("auth.confirm_email", token=token, _external=True)
        html = """\
        <html>
        <body>
            <p>Click this link to verify your account<br>
            <a href="{}">Confirm</a> 
            </p>
        </body>
        </html>
        """.format(
            link
        )
        send_email(email, "Email verification", html)
        user.email = email
        db.session.commit()
        flash("Please check your email to confirm", category="success")
        return redirect(url_for("main.profile"))
    form.email.default = user.email
    form.process()
    return render_template("auth/verify_email.html", form=form)


@auth_bp.route("/confirm_email/<token>")
def confirm_email(token):
    if token:
        try:
            username = loads_token(token, 1800, "verify_email_address")
            user = db.session.query(User).filter(User.username == username).first()
            user.is_email_verified = True
            db.session.commit()
            return "Congratulation! Your account is now verified. You can now close this site"
        except SignatureExpired:
            abort(401)
    else:
        abort(403)

@auth_bp.route("/change_email", methods=["POST", "GET"])
@require_login
def change_email():
    user = load_user()
    if not user.is_email_verified:
        return redirect(url_for("auth.verify_email"))
    form = ChangeEmailVerification(user)
    if form.validate_on_submit():
        email = form.email.data
        data = dict(username=user.username, email=email)
        token = dumps_token(data, "change_email")
        link = url_for("auth.update_email", token=token, _external=True)
        html = """\
        <html>
        <body>
            <p>Click this link to change your email<br>
            <a href="{}">Change</a>
            </p>
        </body>
        </html>
        """.format(
            link
        )
        send_email(email, "Change Email", html)
        flash("Please check your email to change your email", category="success")
        return redirect(url_for("main.profile"))
    return render_template("auth/change_email.html", form=form)


@auth_bp.route("/update_email/<token>", methods=["GET", "POST"])
def update_email(token):
    if token:
        try:
            data = loads_token(token, max_age=1800, salt="change_email")
            user = User.query.filter_by(username=data["username"]).first()
            user.email = data["email"]
            db.session.commit()
        except SignatureExpired:
            abort(401)
    return "<h1>Your Email change successfully. You may now close this page</h1>"


