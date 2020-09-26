from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from config import Config
from app.auth.models import User
import notion


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    notion_id = StringField('ID', validators=[DataRequired()])
    admin = BooleanField('Admin')
    submit = SubmitField('Save changes')

    def validate_notion_id(self, notion_id):
        user = User.query.filter_by(notion_id=notion_id.data).first()
        block = Config.notion_client.get_block(notion_id.data)
        if type(block) is not notion.collection.CollectionRowBlock:
            raise ValidationError('Invalid ID')
