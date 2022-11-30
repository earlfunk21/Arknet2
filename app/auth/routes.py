
from flask import abort, flash, redirect, render_template, url_for, request
from itsdangerous import BadSignature, SignatureExpired
from app.auth import auth_bp
from app.auth.forms import *
from app.auth.utils import *
from app.models import SecretQuestion, db, UserDetails, User, EmailAddress
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
        user = {'username': username, 'password': password}
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
        user = User(username=token['username'],
                    password=token['password'],
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
    if user.secret_question is None:
        flash("Secret question is not yet setup.", "warning")
        return redirect(url_for('auth.update_secret_question'))
    form = UpdatePasswordForm(user)
    if form.validate_on_submit():
        password = form.password.data
        user.password = password
        user.last_modified = db.func.now()
        db.session.commit()
        flash("Password updated successfully", "success")
        return redirect(url_for('auth.logout'))
    return render_template("auth/update_password.html", form=form, question=user.secret_question.question)



@auth_bp.route("/secret_question/", methods=["GET", "POST"])
@require_login
def update_secret_question():
    user = load_user()
    form = UpdateSecretQuestion()
    if user.secret_question:
        form.question.data = user.secret_question.question
    if form.validate_on_submit():
        question = request.form.get('question')
        answer = request.form.get('answer')
        if user.secret_question:
            user.secret_question.question = question
            user.secret_question.answer = answer
        else:
            secret_question = SecretQuestion(question = question, answer = answer)
            user.secret_question = secret_question
        db.session.commit()
        return redirect(url_for('main.profile'))
    return render_template("auth/update_sq.html", form=form)


@auth_bp.route("/verify_email/", methods=["GET", "POST"])
@require_login
def verify_email():
    user = load_user()
    form = VerifyEmailAddress()
    if form.validate_on_submit():
        email = form.email.data
        if user.email_address is not None:
            user.email_address = email
        else:
            user.email_address = EmailAddress(email=email)
        token = dumps_token(user.username, "verify_email_address")
        link = url_for("auth.confirm_email", token=token, _external=True)
        html = """\
        <html>
        <body>
            <p>Click this link to verify your account<br>
            <a href="{}">Confirm</a> 
            has many great tutorials.
            </p>
        </body>
        </html>
        """.format(link)
        send_email(email, "Email verification", html)
        db.session.commit()
        flash("Please check your email to confirm", category="success")
        return redirect(url_for("main.profile"))
    form.email.default = user.email_address
    form.process()
    return render_template("auth/verify_email.html", form=form)


@auth_bp.route("/confirm_email/<token>")
def confirm_email(token):
    if token:
        try:
            username = loads_token(token, 1800, "verify_email_address")
            user = db.session.query(User).filter(User.username == username).first()
            user.email_address.is_verified = True
            db.session.commit()
            return "Congratulation! Your account is now verified. You can now close this site"
        except SignatureExpired:
            flash("Link is expired")
    else:
        abort(403)