from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from time import time
import jwt
from config import Config
from app.email import send_email
import traceback
import sys
import datetime
from notion.collection import NotionDate

db = SQLAlchemy()

login = LoginManager()
login.login_view = 'auth.login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    course = db.Column(db.String(128))
    notion_id = db.Column(db.String(256))
    admin = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_id(self, notion_id):
        self.notion_id = notion_id
        self.username = Config.notion_client.get_block(notion_id).title

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_sessions(self):
        page = Config.notion_client.get_block(self.notion_url)
        sessions_list = []
        for session in page.sessions:
            details = {'id': sessions.id, 'title': session.title, 'date': session.date.start}
            sessions_list.append(details)
        return sessions_list

    def get_upcoming_sessions(self):
        sessions = self.get_sessions()

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, Config.SECRET_KEY, algorithm='HS256').decode('utf-8')

    def add_session(self, start_time, course, zoom_link=None):
        try:
            student = Config.notion_client.get_block(self.notion_id)
            sessions = Config.sessions.collection
            # course = Config.notion_client.get_block(Config.subjects[course]['id']).title
            count = 0
            for session in sessions.get_rows():
                if len(session.student) > 0:
                    if session.student[0].title == student.title:
                        count += 1
            title = '{} {}'.format(student.title, count)
            start_time = start_time.replace(':', '')
            date = NotionDate(datetime.datetime.strptime(start_time, '%Y-%m-%dT%H%M%S%z'))
            row = sessions.add_row(title = title, student=student, subject=course, date=date)
            #send_email('Session created', 'Ben', ['bamiesking@gmail.com'], title, title)
        except Exception:
            var = sys.exc_info()
            #tb = str(traceback.format_exception(*var))
            tb = traceback.format_exc()
            send_email('Session failed', 'Ben', ['bamiesking@gmail.com'], tb, tb)

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
