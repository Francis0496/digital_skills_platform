import pytest


def login(client, email="learner@example.com"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": "SecurePass123!"},
        follow_redirects=True,
    )


def test_design_01_public_navigation_has_mobile_control(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'aria-controls="mobile-menu"' in response.data
    assert b"Courses" in response.data
    assert b"coming later" not in response.data.lower()
    assert b"branding_package/logo-full.svg" in response.data
    assert b"branding_package/favicon-32x32.png" in response.data
    assert b'class="desktop-navigation"' in response.data
    assert b'class="mobile-menu-button menu-button"' in response.data
    assert b'class="hero-actions"' in response.data
    assert b"hero-feature-card" not in response.data
    assert b"?v=2026.08.24.2" in response.data
    for path in (b"/courses/", b"/opportunities/", b"/mentorship/mentors", b"/about"):
        assert path in response.data


def test_design_01b_public_brand_assets_and_about_page_are_served(client):
    for path in (
        "/static/branding_package/logo-full.svg",
        "/static/branding_package/logo-full-white.svg",
        "/static/branding_package/favicon.ico",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.content_length

    about = client.get("/about")
    assert about.status_code == 200
    assert b"A connected pathway into digital work" in about.data


def test_design_01c_authentication_pages_use_brand_and_accessible_fields(client):
    for path, heading in (
        ("/auth/login", b"Welcome back"),
        ("/auth/register", b"Join the platform"),
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert b"branding_package/logo-full-white.svg" in response.data
        assert heading in response.data
        assert b"<label" in response.data


def test_design_02_dashboard_requires_authentication(client):
    response = client.get("/users/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


@pytest.mark.parametrize(
    ("role_name", "visible_label", "hidden_label"),
    (
        ("freelancer", b"My Courses", b"Post Opportunity"),
        ("mentor", b"My Mentees", b"My Applications"),
        ("client", b"My Opportunities", b"Learning Progress"),
        ("administrator", b"Statistics", b"My Mentees"),
    ),
)
def test_design_03_dashboard_navigation_matches_role(
    client, user_factory, role_name, visible_label, hidden_label
):
    user_factory(role_name=role_name)
    response = login(client)

    assert response.status_code == 200
    assert b"Welcome back, Test User" in response.data
    assert visible_label in response.data
    assert hidden_label not in response.data
    assert b'aria-controls="dashboard-sidebar"' in response.data


def test_design_04_unimplemented_dashboard_items_are_not_links(client, user_factory):
    user_factory()
    response = login(client)

    assert b'<span class="sidebar-link sidebar-link-disabled"' in response.data
    assert b"Coming in a later increment" in response.data


def test_design_05_reusable_component_styles_are_served(client):
    response = client.get("/static/css/app.css")
    assert response.status_code == 200
    for component in (b".btn-primary", b".form-input", b".card", b".badge", b".alert"):
        assert component in response.data
    for responsive_rule in (
        b".desktop-navigation { display: none",
        b".mobile-menu-button { display: none",
        b".pathway-grid { grid-template-columns: repeat(4",
        b"box-sizing: border-box",
    ):
        assert responsive_rule in response.data
