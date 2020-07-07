from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import current_user, login_user, logout_user
from .models import User, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, LinkIDForm
from app.email import send_password_reset_email
from config import Config
import traceback


bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.admin:
            return redirect(url_for('admin.panel'))
        return redirect(url_for('panel.panel'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        if current_user.admin:
            return redirect(url_for('admin.panel'))
        return redirect(url_for('panel.panel'))
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('panel.panel'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created", 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title="Register")

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('panel.panel'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            try:
                send_password_reset_email(user)
                flash('Email sent', 'info')
            except Exception as e:
                flash(traceback.format_exc(), 'danger')
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('panel.panel'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, title="Reset Password")

@bp.route('/link_id')
def link_id():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    form = LinkIDForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        user.set_id(form.notion_id.data)
        db.session.add(user)
        db.session.commit()
        flash('ID successfully linked', 'success')
        return redirect(url_for('panel.panel'))
    return render_template('auth/link_id.html', form=form, title="Link ID")

