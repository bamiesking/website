from flask import Flask, render_template
from config import Config

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask_migrate import Migrate
from flask_menu import Menu
from flask_breadcrumbs import Breadcrumbs, default_breadcrumb_root

from app.main import bp as main_bp
from app.auth import bp as auth_bp
from app.errors import not_found_error, internal_server_error
from app.panel import bp as panel_bp
from app.timetable import bp as timetable_bp
from app.admin import bp as admin_bp
from app.calendly import bp as calendly_bp

from app.auth import db as auth_db
from app.auth import login
from app.email import mail

from app.timetable import strip_auth_error
migrate = Migrate()
breadcrumbs = Breadcrumbs()

sentry_sdk.init(
    dsn=Config.SENTRY_DSN,
    integrations=[FlaskIntegration()],
    before_send=strip_auth_error
)


def create_app(config_class=Config):
    # Setup flask app and database
    app = Flask(__name__)
    app.config.from_object(config_class)

    auth_db.init_app(app)
    migrate.init_app(app, auth_db)
    mail.init_app(app)
    login.init_app(app)
    breadcrumbs.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(timetable_bp, url_prefix="/timetable")
    app.register_blueprint(panel_bp, url_prefix="/panel")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(calendly_bp)

    # Register error handlers
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_server_error)

    default_breadcrumb_root(panel_bp, '.')

    return app
