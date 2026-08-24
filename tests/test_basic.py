from flask import Flask, current_app

from app import create_app
from app.extensions import csrf, db, login_manager, migrate
from config import TestingConfig


def test_foundation_01_application_factory_creates_app():
    app = create_app(TestingConfig)
    assert isinstance(app, Flask)
    assert app.testing is True


def test_foundation_02_home_route_returns_200(client):
    assert client.get("/").status_code == 200


def test_foundation_03_home_contains_platform_name(client):
    response = client.get("/")
    assert b"Digital Skills Platform" in response.data


def test_foundation_03b_csp_allows_only_approved_lesson_players(client):
    policy = client.get("/").headers["Content-Security-Policy"]
    assert "frame-src https://www.youtube-nocookie.com https://player.vimeo.com" in policy
    assert "media-src 'self' https:" in policy


def test_foundation_04_unknown_route_uses_custom_404(client):
    response = client.get("/route-that-does-not-exist")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_foundation_05_extensions_initialize(app):
    assert "sqlalchemy" in app.extensions
    assert "migrate" in app.extensions
    assert "csrf" in app.extensions
    assert app.login_manager is login_manager
    assert db is not None and migrate is not None and csrf is not None


def test_foundation_06_all_blueprints_register(app):
    assert set(app.blueprints) == {
        "admin",
        "applications",
        "auth",
        "courses",
        "main",
        "mentorship",
        "notifications",
        "opportunities",
        "portfolio",
        "users",
    }


def test_foundation_07_test_database_is_isolated(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["WTF_CSRF_ENABLED"] is False


def test_foundation_08_error_templates_render(app):
    cases = (
        ("/test-403", 403, b"Access denied"),
        ("/test-500", 500, b"Something went wrong"),
    )

    for path, status, _ in cases:
        endpoint = path.removeprefix("/").replace("-", "_")

        def trigger_error(status_code=status):
            from flask import abort

            abort(status_code)

        app.add_url_rule(path, endpoint, trigger_error)

    for path, status, expected_text in cases:
        response = app.test_client().get(path)
        assert response.status_code == status
        assert expected_text in response.data


def test_create_admin_command_creates_admin_and_rejects_duplicates(app):
    from app.models import User

    runner = app.test_cli_runner()
    command = [
        "create-admin",
        "--full-name",
        "Ibrahim Sorie Kondeh",
        "--email",
        "ibrahimsoriekondeh@gmail.com",
    ]
    result = runner.invoke(args=command, input="SecurePass123!\nSecurePass123!\n")

    assert result.exit_code == 0
    user = db.session.scalar(
        db.select(User).filter_by(email="ibrahimsoriekondeh@gmail.com")
    )
    assert user is not None
    assert user.full_name == "Ibrahim Sorie Kondeh"
    assert user.role_name == "administrator"
    assert user.check_password("SecurePass123!")

    duplicate = runner.invoke(
        args=command, input="AnotherPass123!\nAnotherPass123!\n"
    )
    assert duplicate.exit_code != 0
    assert "already exists" in duplicate.output
