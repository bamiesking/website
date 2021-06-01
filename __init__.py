from flask import Flask
from config import Config

# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

from flask_migrate import Migrate

from app.main import bp as main_bp
from app.errors import not_found_error, internal_server_error
from app.sisyphus import bp as sisyphus_bp

# from app.auth import db as auth_db
# from app.auth import login
# from app.email import mail


migrate = Migrate()

# sentry_sdk.init(
#     dsn=Config.SENTRY_DSN,
#     integrations=[FlaskIntegration()]
# )


def create_app(config_class=Config):
    # Setup Flask app and database
    app = Flask(__name__)
    app.config.from_object(config_class)

    # auth_db.init_app(app)
    # migrate.init_app(app, auth_db)
    # mail.init_app(app)
    # login.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    # app.register_blueprint(auth_bp)
    app.register_blueprint(sisyphus_bp, url_prefix="/sisyphus")

    # Register error handlers
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_server_error)

    return app
