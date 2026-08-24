import logging
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import logout_user

from config import config_by_name
from .extensions import csrf, db, login_manager, migrate


def create_app(config_class=None):
    """Create and configure a Digital Skills Platform application."""
    app = Flask(__name__, instance_relative_config=True)

    if config_class is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")
        config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    if app.config.get("ENV_NAME") == "production":
        secret_key = os.environ.get("SECRET_KEY", "")
        if len(secret_key) < 32:
            raise RuntimeError("Production requires SECRET_KEY with at least 32 characters.")
        app.config["SECRET_KEY"] = secret_key

    os.makedirs(app.instance_path, exist_ok=True)
    app.config.setdefault(
        "PROFILE_UPLOAD_FOLDER", os.path.join(app.instance_path, "uploads", "profiles")
    )
    os.makedirs(app.config["PROFILE_UPLOAD_FOLDER"], exist_ok=True)
    app.config.setdefault("PROJECT_UPLOAD_FOLDER", os.path.join(app.instance_path, "uploads", "projects"))
    os.makedirs(app.config["PROJECT_UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401

    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)
    register_account_checks(app)
    register_security_headers(app)
    configure_logging(app)

    return app


def register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), geolocation=(), microphone=()"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; base-uri 'self'; form-action 'self'; "
            "frame-ancestors 'none'; img-src 'self' data:; object-src 'none'; "
            "script-src 'self'; style-src 'self' 'unsafe-inline'",
        )
        if app.config.get("ENV_NAME") == "production":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response


def register_blueprints(app):
    from .admin import bp as admin_bp
    from .applications import bp as applications_bp
    from .auth import bp as auth_bp
    from .courses import bp as courses_bp
    from .main import bp as main_bp
    from .mentorship import bp as mentorship_bp
    from .notifications import bp as notifications_bp
    from .opportunities import bp as opportunities_bp
    from .portfolio import bp as portfolio_bp
    from .users import bp as users_bp

    for blueprint in (
        main_bp,
        auth_bp,
        users_bp,
        courses_bp,
        portfolio_bp,
        opportunities_bp,
        mentorship_bp,
        notifications_bp,
        admin_bp,
        applications_bp,
    ):
        app.register_blueprint(blueprint)


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def request_too_large(error):
        return render_template("errors/413.html"), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def configure_logging(app):
    if not app.debug and not app.testing:
        app.logger.setLevel(logging.INFO)


def register_commands(app):
    import click

    from .models import seed_roles

    @app.cli.command("seed-roles")
    def seed_roles_command():
        """Create the four approved platform roles."""
        created = seed_roles()
        click.echo(f"Roles ready ({created} created).")


def register_account_checks(app):
    @app.before_request
    def reject_deactivated_sessions():
        from .models import User

        user_id = session.get("_user_id")
        user = db.session.get(User, int(user_id)) if user_id and str(user_id).isdigit() else None
        if user is not None and not user.is_active:
            logout_user()
            flash("This account has been deactivated. Contact an administrator.", "error")
            if request.endpoint != "auth.login":
                return redirect(url_for("auth.login"))
