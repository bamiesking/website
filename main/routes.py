from flask import render_template, flash, redirect, url_for, request, make_response, send_file, Blueprint
from config import Config
from app.email import send_email
from app.calendly import calendly_check_webhook
from app.auth import User
import traceback
import requests
from flask_login import current_user
import json


bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    if 'benatutor.co.uk' in request.url_root:
        return redirect(url_for('panel.panel', id=0))
    return render_template("main/index.html", title='Welcome')


@bp.route("/cv", methods=['GET', 'POST'])
def cv():
    return redirect('https://assets.bamiesking.uk/cv.pdf')


@bp.route("/create_session", methods=['GET', 'POST'])
def create_session():
    user = User.query.filter_by(email='bamiesking@gmail.com').first()
    user.add_session('2020-07-07T00:00:00Z', 'Edexcel iGCSE Physics')
    return 'Done'


@bp.route("/calendly", methods=['GET', 'POST'])
def calendly():
    id = json.dumps(json.loads(calendly_check_webhook().text)['data'][0]['id'])
    if request.headers['User-Agent'] == 'Calendly' and request.headers['X-Calendly-Hook-Id'] == id:
        data = request.json
        if data['payload']['event_type']['name'] == "60 Minute Tutorial":
            user = User.query.filter_by(email=data['payload']['invitee']['email']).first()
            user.add_session(data['payload']['event']['start_time'], str(data['payload']['questions_and_responses']['1_response']))
        return make_response()
    return redirect(url_for('main.index'))

@bp.route("/bookings/tutorial")
def tutorial():
    if current_user.is_authenticated:
        requests.get(url_for('main.calendly', _external=True))
        subject = Config.notion_client.get_block(current_user.notion_id).subject
        return render_template("main/tutorial.html", title="Book a tutorial", subject=subject)
    flash('You must be logged in to book a session', 'info')
    return redirect(url_for('auth.login'))

@bp.route("/bookings/free_meeting")
def free_meeting():
    requests.get(url_for('main.calendly', _external=True))
    return render_template("main/free_meeting.html", title="Book a free meeting")

@bp.route('/tutoring')
def tutoring():
    return render_template("main/tutoring.html", title='Tutoring')

@bp.route('/web')
def web():
    flash('That page is under construction', 'danger')
    return redirect(url_for('.index'))
    # return render_template("main/web.html", title='Web services')

@bp.route('/portfolio')
def portfolio():
    flash('That page is under construction', 'danger')
    return redirect(url_for('.index'))

@bp.route('/margaret')
def margaret():
    return redirect('https://github.com/bamiesking/st-margaret/wiki')

@bp.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0

@bp.route('/debug-mail')
def trigger_email():
    try:
        send_email('Test', 'ben@bamiesking.uk', ['bamiesking@gmail.com'], 'Test', '<h1>Test</h1>')
        flash('Email sent', 'info')
    except Exception as e:
        flash(traceback.format_exc(), 'danger')
    return redirect(url_for('.index'))
