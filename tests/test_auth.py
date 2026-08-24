from app.auth.decorators import roles_required
from app.extensions import db
from app.models import APPROVED_ROLES, Role, User


def register(client, **overrides):
    data = {
        "full_name": "Aminata Kamara",
        "email": "aminata@example.com",
        "role": "freelancer",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    data.update(overrides)
    return client.post("/auth/register", data=data, follow_redirects=True)


def login(client, email="learner@example.com", password="SecurePass123!"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_auth_01_roles_are_seeded(app):
    names = set(db.session.scalars(db.select(Role.name)).all())
    assert names == set(APPROVED_ROLES)


def test_auth_01b_role_seed_is_idempotent(app):
    from app.models import seed_roles

    assert seed_roles() == 0
    assert db.session.scalar(db.select(db.func.count(Role.id))) == 4


def test_auth_02_valid_public_registration(client, app):
    response = register(client)
    user = db.session.scalar(db.select(User).filter_by(email="aminata@example.com"))

    assert response.status_code == 200
    assert b"account has been created" in response.data
    assert user is not None
    assert user.role_name == "freelancer"
    assert user.password_hash != "SecurePass123!"
    assert user.check_password("SecurePass123!")


def test_auth_03_duplicate_email_is_rejected(client, user_factory):
    user_factory(email="aminata@example.com")
    response = register(client)

    assert b"already uses this email" in response.data
    assert db.session.scalar(
        db.select(db.func.count(User.id)).filter_by(email="aminata@example.com")
    ) == 1


def test_auth_04_administrator_cannot_register_publicly(client):
    response = register(client, email="admin@example.com", role="administrator")
    assert b"Not a valid choice" in response.data
    assert db.session.scalar(db.select(User).filter_by(email="admin@example.com")) is None


def test_auth_05_valid_login_and_logout(client, user_factory):
    user_factory()
    response = login(client)
    assert b"Test User" in response.data

    response = client.post("/auth/logout", follow_redirects=True)
    assert b"You have been logged out" in response.data
    assert b"Log in" in response.data


def test_auth_06_invalid_password_is_rejected(client, user_factory):
    user_factory()
    response = login(client, password="incorrect-password")
    assert b"Invalid email address or password" in response.data


def test_auth_07_inactive_account_cannot_login(client, user_factory):
    user_factory(is_active=False)
    response = login(client)
    assert b"account has been deactivated" in response.data


def test_role_01_anonymous_user_is_redirected_to_login(app, client):
    @app.get("/protected")
    @roles_required("freelancer")
    def protected():
        return "allowed"

    response = client.get("/protected")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_role_02_wrong_role_is_forbidden(app, client, user_factory):
    user_factory(role_name="client")

    @app.get("/freelancers-only")
    @roles_required("freelancer")
    def freelancers_only():
        return "allowed"

    login(client)
    response = client.get("/freelancers-only")
    assert response.status_code == 403
    assert b"Access denied" in response.data


def test_role_03_correct_role_is_allowed(app, client, user_factory):
    user_factory()

    @app.get("/learner-area")
    @roles_required("freelancer")
    def learner_area():
        return "allowed"

    login(client)
    response = client.get("/learner-area")
    assert response.status_code == 200
    assert response.data == b"allowed"


def test_auth_08_external_next_url_is_not_followed(client, user_factory):
    user_factory()
    response = client.post(
        "/auth/login?next=https://example.org/unsafe",
        data={"email": "learner@example.com", "password": "SecurePass123!"},
    )
    assert response.headers["Location"].endswith("/users/dashboard")


def test_auth_09_deactivated_existing_session_is_ended(client, user_factory):
    user = user_factory()
    login(client)
    persisted_user = db.session.get(User, user.id)
    persisted_user.is_active = False
    db.session.commit()

    response = client.get("/", follow_redirects=True)
    assert b"account has been deactivated" in response.data
    assert b"Log in" in response.data
