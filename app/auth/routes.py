from flask import abort, flash, redirect, render_template, url_for, request, session
from itsdangerous import BadSignature, SignatureExpired
from app.auth import auth_bp
from app.auth.forms import *
from app.auth.utils import *
from app.auth.utils import admin_required
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


@auth_bp.route("/register/<token>/", methods=["GET", "POST"])
def register(token):
    try:
        token = loads_token(token, max_age=86400, salt="register")
    except SignatureExpired:
        return abort(401)
    except BadSignature:
        return abort(401)

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user_details = UserDetails(
            first_name=token["first_name"],
            middle_name=token["middle_name"],
            last_name=token["last_name"],
            address=token["address"],
            phone=token["phone"],
            social_media=token["social_media"],
        )
        user = User(username=username, password=password, user_details=user_details)
        db.session.add(user)
        db.session.commit()
        flash("Successfully created an account!", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)



@auth_bp.route("/create_subscriber", methods=["GET", "POST"])
@require_login
@admin_required
def create_subscriber():
    form = UserDetailsForm()
    if form.validate_on_submit():
        first_name = form.first_name.data.capitalize()
        middle_name = form.middle_name.data.capitalize()
        last_name = form.last_name.data.capitalize()
        address = form.address.data.title()
        phone = form.phone.data
        social_media = form.social_media.data
        data = dict(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            address=address,
            phone=phone,
            social_media=social_media,
        )
        token = dumps_token(data, salt="register")
        link = url_for("auth.register", token=token, _external=True)
        return redirect(url_for("auth.create_link", link=link))
    return render_template("auth/create_subs.html", form=form)


@auth_bp.route("/create_link")
@require_login
@admin_required
def create_link():
    link = request.args.get("link")
    return render_template("auth/create_subs_link.html", link=link)


@auth_bp.route("/forgot_password/", methods=["GET", "POST"])
@already_login
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = dumps_token(user.username, salt="change_password")
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
        send_email(user.email, "Retrieve Password", html)
        flash("Please check your email to retrieve your password", category="success")
        return redirect(url_for("auth.login", token=token))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/update_password/", defaults={"token": None}, methods=["GET", "POST"])
@auth_bp.route("/update_password/<token>", methods=["GET", "POST"])
def update_password(token):
    user = load_user()
    if token:
        try:
            username = loads_token(token, max_age=1800, salt="change_password")
            user = User.query.filter_by(username=username).first()
        except SignatureExpired:
            abort(401)
    if not user:
        return redirect(url_for("auth.change_password"))
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
            flash("Congratulation! Your account is now verified!", "success")
            return redirect(url_for("main.profile"))
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
    flash(f"Your Email change to {user.hide_email()} successfully.", "success")
    return redirect(url_for("main.profile"))
