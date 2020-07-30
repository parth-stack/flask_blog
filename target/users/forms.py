from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from target.models import User

class RegisterForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(2,10)])
    email=StringField('Email',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired(),Length(5)])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up') 
    # custom validator of format[validate_XYZ] raises ValidationError
    def validate_username(self,n):
        user=User.query.filter_by(username=n.data).first()
        if user:
            raise ValidationError('the username is taken please choose a different one')
    def validate_email(self,e):
        user=User.query.filter_by(email=e.data).first()
        if user:
            raise ValidationError('the email is taken please choose a different one')

class UpdateForm(FlaskForm):
    username=StringField('Username')
    email=StringField('Email')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit=SubmitField('Update')

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')