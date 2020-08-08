from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from config import Config
from app.auth.models import User
import notion

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Account with this email address already exists')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class LinkIDForm(FlaskForm):
    notion_id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Link')
    
    def validate_notion_id(self, notion_id):
        user = User.query.filter_by(notion_id=notion_id.data).first()
        if user is not None:
            raise ValidationError('Account with this ID already exists')
        try:
            block = Config.notion_client.get_block(notion_id.data)
            if type(block) is not notion.collection.CollectionRowBlock:
                raise ValidationError('Invalid ID')
        except:
            raise ValidationError('Invalid ID')