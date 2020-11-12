from flask import Blueprint, redirect, render_template, url_for, request, make_response, flash
from flask_login import current_user
from datetime import datetime, timedelta
from config import Config
from .methods import generate_signature
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb, default_breadcrumb_root

bp = Blueprint('panel', __name__)


# Dynamic list constructors for breadcrumb decorators
def panel_dlc(*args, **kwargs):
    text = 'Home'
    panel_id = None
    if 'panel_id' in request.view_args:
        panel_id = request.view_args['panel_id']
        if type(panel_id) == str:
            notion_data = Config.notion_client.get_block(panel_id)
            text = notion_data.title
    return [{'text': text, 'url': url_for('panel.panel', panel_id=panel_id)}]


def session_dlc(*args, **kwargs):
    session_id = None
    text = 'Session'
    if 'session_id' in request.view_args:
        panel_id = request.view_args['panel_id']
        session_id = request.view_args['session_id']
        notion_data = Config.notion_client.get_block(session_id)
        text = 'Session {}'.format(notion_data.title.split(' ')[-1])
    return [{'text': text, 'url': url_for('panel.session', session_id=session_id, panel_id=panel_id)}]


def resource_dlc(*args, **kwargs):
    resource_id = None
    text = 'Resource'
    if 'resource_id' in request.view_args:
        panel_id = request.view_args['panel_id']
        resource_id = request.view_args['resource_id']
        notion_data = Config.notion_client.get_block(resource_id)
        text = notion_data.title
    return [{'text': text, 'url': url_for('panel.resource', resource_id=resource_id, panel_id=panel_id)}]


@bp.route('/', defaults={'panel_id': None})
@bp.route('/<panel_id>')
@register_breadcrumb(bp, '.', '', dynamic_list_constructor=panel_dlc)
def panel(panel_id):
    if panel_id is None:
        if current_user.is_authenticated:
            if current_user.notion_id is not None:
                panel_id = current_user.notion_id
            else:
                flash('No ID linked to your account', 'danger')
                return redirect(url_for('auth.link_id'))
        elif 'id_hash' in request.cookies:
            panel_id = request.cookies.get('id_hash')
        else:
            flash('Please login or use a valid panel link', 'danger')
            return redirect(url_for('auth.login'))
        return redirect(url_for('panel.panel', panel_id=panel_id))

    resp = make_response(render_template('panel/panel.html', id=panel_id, title="Panel"))
    resp.set_cookie('id_hash', panel_id)
    return resp

@bp.route('/card/<card>/<id>', methods=['GET', 'POST'])
def card(card, id):

    # Fetch notion data
    notion_data = Config.notion_client.get_block(id)

    # Initialise response object
    data = None

    if card == 'progress':
        # Calculate number of covered and revised topics, and completed exercises
        covered_topics = {}
        revised_topics = {}
        completed_exercises = {}
        marked_exercises = {}

        # Initialise
        for subject in notion_data.subject:
            covered_topics[subject] = []
            revised_topics[subject] = []
            completed_exercises[subject] = []
            marked_exercises[subject] = []

        # Add each completed session to the relevant dictionary
        for session in notion_data.sessions:
            for lesson_plan in session.lesson_plan:
                try:
                    if session.revision:
                        revised_topics[lesson_plan.subject].append(lesson_plan.title)
                    else:
                        covered_topics[lesson_plan.subject].append(lesson_plan.title)
                except:
                    pass

        for child in notion_data.children:
            if child.type == 'collection_view' and child.title in ['Assignments', 'Assessments']:
                for row in child.collection.get_rows():
                    for resource in row.resource:
                        subjects = resource.subject
                        for subject in subjects:
                            try:
                                completed_exercises[subject].append(row.title)
                                if row.marked:
                                    marked_exercises[subject].append(row.title)
                            except:
                                pass

        for subject in notion_data.subject:
            covered_topics[subject] = len(set(covered_topics[subject]))
            revised_topics[subject] = len(set(revised_topics[subject]))
            completed_exercises[subject] = len(set(completed_exercises[subject]))
            marked_exercises[subject] = len(set(marked_exercises[subject]))

        data = {
            'subject': notion_data.subject,
            'subjects': Config.subjects,
            'covered_topics': covered_topics,
            'revised_topics': revised_topics,
            'completed_exercises': completed_exercises,
            'marked_exercises': marked_exercises
        }

    if card == "details":
        data = {'title': notion_data.title,
                'subject': notion_data.subject,
                'subjects': Config.subjects
                }

    if card == "sessions":
        data = []
        for session in notion_data.sessions:
            if session.date is not None:
                if isinstance(session.date.start, type(datetime.now())):
                    if datetime.now() < session.date.start:
                        entry = [session.title.split(' ')[-1],
                                 session.date.start.strftime("%d/%m/%y  %H:%M"),
                                 session.id.replace('-', '')]
                        data.append(entry)
                elif isinstance(session.date.start, type(datetime.today())):
                    if datetime.today() <= session.date.start:
                        entry = [session.title.split(' ')[-1],
                                 session.date.start.strftime("%d/%m/%y"),
                                 session.id.replace('-', '')]
                        data.append(entry)

    if card == 'assignments':
        data = []
        for s in notion_data.children:
            if s.type == 'collection_view' and s.title == 'Assignments':
                for row in s.collection.get_rows():
                    if row.submitted_solution == []:
                        data.append(row)

    if card == 'assessments':
        data = []
        for s in notion_data.children:
            if s.type == 'collection_view' and s.title == 'Assessments':
                for row in s.collection.get_rows():
                    if row.submitted_solution == []:
                        data.append(row)

    if card == 'returned':
        data = []
        for s in notion_data.children:
            if s.type == 'collection_view':
                for row in s.collection.get_rows():
                    if row.marked:
                        data.append(row)

    return render_template('panel/cards/{}.html'.format(card), data=data, panel_id=id)


@bp.route('/<panel_id>/session/<session_id>')
@register_breadcrumb(bp, '.session', '', dynamic_list_constructor=session_dlc)
def session(panel_id, session_id):
    notion_data = Config.notion_client.get_block(session_id)
    data = {
        'notion': notion_data,
        'title': 'Session {}: {}'.format(notion_data.title.split(' ')[-1], notion_data.date.start.strftime("%d/%m/%y"))
    }
    return render_template('panel/session.html', session=data, title=data['title'])

@bp.route('/<panel_id>/resource/<resource_id>')
@register_breadcrumb(bp, '.resource', '', dynamic_list_constructor=resource_dlc)
def resource(panel_id, resource_id):
    notion_data = Config.notion_client.get_block(resource_id)
    data = {
        'notion': notion_data,
        'title': notion_data.title
    }
    return render_template('panel/resource.html', session=data, title=data['title'])

@bp.route('/<panel_id>/assignment/<resource_id>')
@register_breadcrumb(bp, '.assignment', '', dynamic_list_constructor=resource_dlc)
def assignment(panel_id, resource_id):
    notion_data = Config.notion_client.get_block(resource_id)
    data = {
        'notion': notion_data,
        'title': notion_data.title
    }
    return render_template('panel/assignment.html', session=data, panel_id=panel_id, type=typ)

@bp.route('/<panel_id>/meeting/<id>/<password>')
def meeting(panel_id, id, password):
    data = {'apiKey': Config.ZOOM_KEY, 'apiSecret': Config.ZOOM_SECRET, 'meetingNumber': id, 'role': 0}
    signature = generate_signature(data)
    return render_template('panel/zoom.html', api=data['apiKey'], signature=signature, id=id, password=password, sentry_dsn=Config.SENTRY_DSN)












