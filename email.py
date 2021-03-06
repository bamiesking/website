from flask_mail import Mail, Message
from config import Config
from flask import render_template

mail = Mail()


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Tutoring Panel] Reset your password',
               sender=Config.ADMINS[0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user,
                                         token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user,
                                         token=token))
