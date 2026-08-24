import pytest

from app import create_app
from app.extensions import db
from app.models import Role, User, seed_roles
from config import TestingConfig


@pytest.fixture()
def app(tmp_path):
    test_app = create_app(TestingConfig)
    upload_folder = tmp_path / "profile-uploads"
    upload_folder.mkdir()
    test_app.config["PROFILE_UPLOAD_FOLDER"] = str(upload_folder)
    project_folder = tmp_path / "project-uploads"
    project_folder.mkdir()
    test_app.config["PROJECT_UPLOAD_FOLDER"] = str(project_folder)

    with test_app.app_context():
        db.create_all()
        seed_roles()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_factory(app):
    def create_user(
        email="learner@example.com",
        password="SecurePass123!",
        role_name="freelancer",
        is_active=True,
    ):
        role = db.session.scalar(db.select(Role).filter_by(name=role_name))
        user = User(
            full_name="Test User",
            email=email,
            role=role,
            is_active=is_active,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    return create_user
