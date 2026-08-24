from pathlib import Path

import pytest

from app import create_app
from config import ProductionConfig


def test_health_check_reports_database_ready(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_security_headers_are_added(client):
    response = client.get("/")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["Permissions-Policy"] == (
        "camera=(), geolocation=(), microphone=()"
    )


def test_production_requires_an_explicit_strong_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="at least 32 characters"):
        create_app(ProductionConfig)


def test_production_enables_transport_and_cookie_protection(monkeypatch, tmp_path):
    secret = "production-secret-that-is-longer-than-32-characters"
    monkeypatch.setenv("SECRET_KEY", secret)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'production.db'}")
    app = create_app(ProductionConfig)

    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.headers["Strict-Transport-Security"].startswith("max-age=")
    assert app.config["SECRET_KEY"] == secret
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_templates_use_local_css_and_csp_safe_event_binding():
    project_root = Path(__file__).parents[1]
    template_root = project_root / "app" / "templates"
    base = (template_root / "base.html").read_text(encoding="utf-8")
    templates = "\n".join(
        path.read_text(encoding="utf-8") for path in template_root.rglob("*.html")
    )

    assert "cdn.tailwindcss.com" not in base
    assert "css/tailwind.css" in base
    assert "onsubmit=" not in templates
    assert (project_root / "app" / "static" / "css" / "tailwind.css").stat().st_size > 0
