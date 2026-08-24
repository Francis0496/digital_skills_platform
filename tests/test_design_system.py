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
    assert b"coming later" in response.data


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
