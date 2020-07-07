from flask import Blueprint, redirect, render_template, url_for, request, make_response, flash
from flask_login import current_user
from datetime import datetime
from config import Config
from .forms import EditUserForm
from app.auth import User, db


bp = Blueprint('admin', __name__)


@bp.route('/')
def panel():
    if not current_user.is_authenticated or not current_user.admin:
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('admin/panel.html', details=[current_user.username, current_user.email],users=users)


@bp.route('/page/<title>')
def page(title):
    if not current_user.is_authenticated or not current_user.admin:
        return redirect(url_for('main.index'))
    return render_template('admin/base.html')


@bp.route('/user/<email>', methods=['GET', 'POST'])
def user(email):
    if not current_user.is_authenticated or not current_user.admin:
        return redirect(url_for('main.index'))
    user = User.query.filter_by(email=email).first()
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.notion_id = form.notion_id.data
        user.admin = form.admin.data
        db.session.commit()
        flash("Changes saved", 'info')
    return render_template('admin/user.html', form=form)


@bp.route('/isadmin')
def isadmin():
    if not current_user.is_authenticated or not current_user.admin:
        return str(False)
    return str(True)
