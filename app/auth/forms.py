
from flask_wtf import FlaskForm
from wtforms import StringField, validators, PasswordField, SelectField, EmailField

from app.models import User
from app.utils import captcha_validator


class RegistrationForm(FlaskForm):
    username = StringField("Username", [validators.InputRequired(),
                                            validators.Length(min=3, max=120, message="Username length must be between %(min)d and %(max)d characters"),
                                            validators.Regexp("^[A-Za-z0-9]+$", message="Username must not contain special characters")])
    password = PasswordField("Password", validators=[validators.InputRequired(),
                                                   validators.Length(min=8, max=120)],
                             render_kw={'data-bs-toggle':"tooltip", 'data-bs-placement': "right", 'title': "Password length must be between 8 and 120 characters"})
    confirm_password = PasswordField("Confirm Password", validators=[validators.InputRequired(),
                                                                             validators.EqualTo("password", message="Password must match")])
    
    def validate_username(form, field):
        if User.query.filter_by(username=field.data).first():
            raise validators.ValidationError(f"{field.data} already exists")
   
        
class LoginForm(FlaskForm):
    
    username = StringField("Username", validators=[validators.DataRequired(message="Please enter your username")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please enter your password")])
    captcha = StringField("Captcha", validators=[captcha_validator])
    
    def validate_username(form, field):
        if not User.query.filter_by(username=field.data).first():
            raise validators.ValidationError(f"{field.data} doesn't exist!")
    

class UpdatePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[validators.InputRequired(),
                                                   validators.Length(min=8, max=120)],
                             render_kw={'data-bs-toggle':"tooltip", 'data-bs-placement': "right", 'title': "Password length must be between 8 and 120 characters"})
    
    confirm_password = PasswordField("Confirm Password", validators=[validators.EqualTo("password", message="Password must match")])
    answer = StringField("Your answer", validators=[validators.InputRequired()])
    
    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def validate_answer(form, field):
        secret_question = SecretQuestion.query.filter_by(user=form.user).first()
        if not secret_question.answer == field.data:
            raise validators.ValidationError(f"Secret answer is incorrect")
    


class ForgotPasswordForm(FlaskForm):
    
    username = StringField("Username", validators=[validators.InputRequired()])
    
    def validate_username(form, field):
        if not User.query.filter_by(username=field.data).first():
            raise validators.ValidationError(f"{field.data} doesn't exist!")


class UserDetailsForm(FlaskForm):
    first_name = StringField("First Name", validators=[validators.InputRequired()])
    middle_name = StringField("Middle Name")
    last_name = StringField("Last Name", validators=[validators.InputRequired()])
    address = StringField("Address", validators=[validators.InputRequired()])
    phone = StringField("Phone Number", validators=[validators.InputRequired()])
    social_media = StringField("Facebook name")


class UpdateSecretQuestion(FlaskForm):
    question = SelectField('Select Secret Question', choices=[('What is the name of your favorite pet?'),
                                                    ('In what city were you born?'),
                                                    ("What is your mother's maiden name?"),
                                                    ('What high school did you attend?'),
                                                    ('What was the name of your elementary school?'),
                                                    ('What was the make of your first car?'),
                                                    ('What was your favorite food as a child?')])
    
    answer = StringField("Answer", validators=[validators.InputRequired()])


class VerifyEmailAddress(FlaskForm):
    email = EmailField("Email Address", validators=[validators.InputRequired(), validators.Email()])
