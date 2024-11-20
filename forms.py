from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email
from flask_wtf import FlaskForm

class RegisterForm(FlaskForm):
    """Renders User Registration Form"""
    username = StringField(
        "Username",
        validators=[InputRequired(), 
                    Length(min=1, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )
    email = StringField(
        "Email",
        validators=[InputRequired(),
                    Email(),
                    Length(max=50)]
    )
    first_name = StringField(
        "First Name",
        validators=[InputRequired(),
                    Length(max=30)]
    )
    last_name = StringField(
        "Last Name",
        validators=[InputRequired(),
                    Length(max=30)]
    )


class LoginForm(FlaskForm):
    """Renders User Login Form"""
    username = StringField(
        "Username",
        validators=[InputRequired(),
                    Length(min=1, max=20)]
    )
    password = PasswordField(
                "Password",
        validators=[InputRequired()]
    )


class FeedbackForm(FlaskForm):
    """Renders Feedback Form"""
    title = StringField(
        "Title",
        validators=[InputRequired(),
                    Length(min=1, max=100)]
    )
    content = StringField(
        "Content",
        validators=[InputRequired()]
    )