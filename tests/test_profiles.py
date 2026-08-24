from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import MentorProfile, Skill, User, UserSkill


def login(client, email="learner@example.com"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": "SecurePass123!"},
        follow_redirects=True,
    )


def profile_data(**overrides):
    data = {
        "full_name": "Updated User",
        "email": "learner@example.com",
        "phone": "+232 76 123456",
        "location": "Freetown",
        "bio": "Digital professional building practical experience.",
    }
    data.update(overrides)
    return data


def image_upload(fmt="PNG", filename="profile.png", size=(32, 32)):
    stream = BytesIO()
    Image.new("RGB", size, color=(67, 56, 202)).save(stream, fmt)
    stream.seek(0)
    return stream, filename


def test_profile_01_anonymous_profile_access_redirects(client):
    for path in ("/users/profile", "/users/profile/edit", "/users/skills"):
        response = client.get(path)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]


def test_profile_02_user_can_update_own_profile(client, user_factory):
    user = user_factory()
    login(client)
    response = client.post("/users/profile/edit", data=profile_data(), follow_redirects=True)
    updated = db.session.get(User, user.id)

    assert response.status_code == 200
    assert b"profile has been updated" in response.data
    assert updated.full_name == "Updated User"
    assert updated.phone == "+232 76 123456"
    assert updated.location == "Freetown"


def test_profile_03_duplicate_email_is_rejected(client, user_factory):
    user_factory()
    user_factory(email="second@example.com", role_name="client")
    login(client)

    response = client.post(
        "/users/profile/edit",
        data=profile_data(email="SECOND@example.com"),
    )
    assert response.status_code == 200
    assert b"already uses this email" in response.data


def test_profile_04_valid_image_is_reencoded_and_served(client, user_factory, app):
    user = user_factory()
    login(client)
    response = client.post(
        "/users/profile/edit",
        data={**profile_data(), "profile_image": image_upload()},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    updated = db.session.get(User, user.id)

    assert response.status_code == 200
    assert updated.profile_image.endswith(".webp")
    stored = Path(app.config["PROFILE_UPLOAD_FOLDER"], updated.profile_image)
    assert stored.is_file()
    with Image.open(stored) as image:
        assert image.format == "WEBP"
        assert image.width <= 800 and image.height <= 800
    assert client.get(f"/users/profile-image/{updated.profile_image}").status_code == 200


def test_profile_05_fake_image_content_is_rejected(client, user_factory):
    user = user_factory()
    login(client)
    response = client.post(
        "/users/profile/edit",
        data={
            **profile_data(),
            "profile_image": (BytesIO(b"not an image"), "profile.png"),
        },
        content_type="multipart/form-data",
    )
    assert b"not a valid JPG, PNG, or WebP image" in response.data
    assert db.session.get(User, user.id).profile_image is None


def test_profile_06_disallowed_image_extension_is_rejected(client, user_factory):
    user_factory()
    login(client)
    response = client.post(
        "/users/profile/edit",
        data={
            **profile_data(),
            "profile_image": (BytesIO(b"content"), "profile.svg"),
        },
        content_type="multipart/form-data",
    )
    assert b"Upload a JPG, PNG, or WebP image" in response.data


def test_profile_07_authenticated_user_can_fetch_another_users_avatar(
    client, user_factory, app
):
    user_factory()
    other = user_factory(email="other@example.com", role_name="client")
    other.profile_image = "other.webp"
    db.session.commit()
    Path(app.config["PROFILE_UPLOAD_FOLDER"], other.profile_image).write_bytes(b"avatar")
    login(client)
    response = client.get(f"/users/avatar/{other.id}")
    assert response.status_code == 200
    assert response.data == b"avatar"


def test_profile_07b_anonymous_avatar_access_is_limited_to_mentors(
    client, user_factory, app
):
    mentor = user_factory(email="mentor-avatar@example.com", role_name="mentor")
    learner = user_factory(email="learner-avatar@example.com")
    mentor.profile_image = "mentor.webp"
    learner.profile_image = "learner.webp"
    db.session.commit()
    Path(app.config["PROFILE_UPLOAD_FOLDER"], mentor.profile_image).write_bytes(b"mentor")
    Path(app.config["PROFILE_UPLOAD_FOLDER"], learner.profile_image).write_bytes(b"learner")

    assert client.get(f"/users/avatar/{mentor.id}").status_code == 200
    assert client.get(f"/users/avatar/{learner.id}").status_code == 404


def test_profile_08_replacing_image_removes_previous_file(client, user_factory, app):
    user = user_factory()
    login(client)
    client.post(
        "/users/profile/edit",
        data={**profile_data(), "profile_image": image_upload()},
        content_type="multipart/form-data",
    )
    first_name = db.session.get(User, user.id).profile_image
    first_path = Path(app.config["PROFILE_UPLOAD_FOLDER"], first_name)
    assert first_path.is_file()

    client.post(
        "/users/profile/edit",
        data={
            **profile_data(),
            "profile_image": image_upload(fmt="JPEG", filename="new-photo.jpg"),
        },
        content_type="multipart/form-data",
    )
    second_name = db.session.get(User, user.id).profile_image
    assert second_name != first_name
    assert not first_path.exists()
    assert Path(app.config["PROFILE_UPLOAD_FOLDER"], second_name).is_file()


def test_skill_01_freelancer_can_add_and_remove_skill(client, user_factory):
    user = user_factory()
    skill = Skill(name="Web Development", description="Build accessible websites")
    db.session.add(skill)
    db.session.commit()
    login(client)

    response = client.post(
        "/users/skills",
        data={"skill_id": skill.id, "proficiency_level": "Intermediate"},
        follow_redirects=True,
    )
    association = db.session.scalar(db.select(UserSkill).filter_by(user_id=user.id))
    assert b"Skill added" in response.data
    assert association.proficiency_level == "Intermediate"

    response = client.post(
        f"/users/skills/{association.id}/remove", follow_redirects=True
    )
    assert b"Skill removed" in response.data
    assert db.session.get(UserSkill, association.id) is None


def test_skill_02_duplicate_skill_is_rejected(client, user_factory):
    user = user_factory()
    skill = Skill(name="Graphic Design")
    db.session.add_all([skill])
    db.session.flush()
    db.session.add(UserSkill(user=user, skill=skill, proficiency_level="Beginner"))
    db.session.commit()
    login(client)

    response = client.post(
        "/users/skills",
        data={"skill_id": skill.id, "proficiency_level": "Advanced"},
    )
    assert b"already added this skill" in response.data


def test_skill_03_invalid_proficiency_is_rejected(client, user_factory):
    user = user_factory()
    skill = Skill(name="Data Analysis")
    db.session.add(skill)
    db.session.commit()
    login(client)

    client.post(
        "/users/skills",
        data={"skill_id": skill.id, "proficiency_level": "Expert"},
    )
    assert db.session.scalar(db.select(UserSkill).filter_by(user_id=user.id)) is None


@pytest.mark.parametrize("role_name", ("mentor", "client", "administrator"))
def test_skill_04_non_freelancers_are_forbidden(client, user_factory, role_name):
    user_factory(role_name=role_name)
    login(client)
    assert client.get("/users/skills").status_code == 403


def test_skill_05_user_cannot_remove_another_users_skill(client, user_factory):
    user_factory()
    other = user_factory(email="other@example.com")
    skill = Skill(name="Content Writing")
    association = UserSkill(user=other, skill=skill, proficiency_level="Advanced")
    db.session.add_all([skill, association])
    db.session.commit()
    login(client)

    assert client.post(f"/users/skills/{association.id}/remove").status_code == 403
    assert db.session.get(UserSkill, association.id) is not None


def test_skill_06_database_prevents_duplicate_associations(app, user_factory):
    user = user_factory()
    skill = Skill(name="Photography")
    db.session.add(skill)
    db.session.flush()
    db.session.add_all(
        [
            UserSkill(user=user, skill=skill, proficiency_level="Beginner"),
            UserSkill(user=user, skill=skill, proficiency_level="Advanced"),
        ]
    )
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_mentor_01_mentor_can_create_and_update_profile(client, user_factory):
    user = user_factory(role_name="mentor")
    login(client)
    response = client.post(
        "/users/mentor-profile/edit",
        data={
            "professional_title": "Software Engineer",
            "expertise": "Web development and career guidance",
            "experience": "Eight years in technology",
            "availability": "Saturday mornings",
        },
        follow_redirects=True,
    )
    mentor_profile = db.session.scalar(
        db.select(MentorProfile).filter_by(user_id=user.id)
    )
    assert response.status_code == 200
    assert b"mentor profile has been updated" in response.data
    assert mentor_profile.professional_title == "Software Engineer"


@pytest.mark.parametrize("role_name", ("freelancer", "client", "administrator"))
def test_mentor_02_non_mentors_are_forbidden(client, user_factory, role_name):
    user_factory(role_name=role_name)
    login(client)
    assert client.get("/users/mentor-profile/edit").status_code == 403


def test_mentor_03_database_allows_only_one_profile_per_mentor(app, user_factory):
    user = user_factory(role_name="mentor")
    db.session.add_all([MentorProfile(user_id=user.id), MentorProfile(user_id=user.id)])
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
