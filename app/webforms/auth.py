import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SubmitField
from wtforms.validators import EqualTo, Length, InputRequired
from werkzeug.security import check_password_hash
from ..utils import db
from ..models import User


class SignupForm(FlaskForm):
    email = StringField(
        label="Email",
        validators=[
            InputRequired(message="Email is required"),
            Length(
                5,
                255,
                message="Email should be at least 5 characters and not more than 255 characters.",
            ),
        ],
    )
    password = PasswordField(
        label="Password",
        validators=[
            InputRequired(message="Password is required"),
            Length(8, 255, message="Password should be at least 8 characters."),
        ],
    )
    confirm_password = PasswordField(
        label="Confirm Password",
        validators=[
            InputRequired(message="Confirm Password is required"),
            EqualTo("password", message="Passwords do not match"),
        ],
    )
    submit = SubmitField(label="Submit")

    def validate_email(self, field):
        if User.check_email(self.email.data):
            raise validators.ValidationError("Email already exist.")

    def is_valid_email(self):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(email_regex, self.email.data) is None:
            raise validators.ValidationError("Invalid Email provided.")


class LoginForm(FlaskForm):
    email = StringField(
        label="Email",
        validators=[validators.InputRequired(message="Email is required.")],
    )
    password = PasswordField(
        label="Password",
        validators=[validators.InputRequired(message="passwor is required.")],
    )
    submit = SubmitField(label="Login")

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()

    def validate_login(self):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError("Login failed. Email not found.")

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError("Invalid password")
