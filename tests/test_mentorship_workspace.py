import pytest

from app.extensions import db
from app.models import (
    Mentorship,
    MentorshipFeedback,
    MentorshipGoal,
    MentorshipProgressUpdate,
    Notification,
)


def login(client, email="learner@example.com"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": "SecurePass123!"},
        follow_redirects=True,
    )


@pytest.fixture()
def workspace_relationship(user_factory):
    learner = user_factory()
    learner.full_name = "Mariama Conteh"
    mentor = user_factory(email="mentor@example.com", role_name="mentor")
    mentor.full_name = "Mohamed Kamara"
    mentorship = Mentorship(freelancer=learner, mentor=mentor, status="active")
    db.session.add(mentorship)
    db.session.commit()
    return mentorship, learner, mentor


def test_workspace_01_participants_can_access_private_active_workspace(
    client, workspace_relationship
):
    mentorship, learner, mentor = workspace_relationship
    assert client.get(f"/mentorship/{mentorship.id}/workspace").status_code == 302

    login(client, learner.email)
    learner_view = client.get(f"/mentorship/{mentorship.id}/workspace")
    assert learner_view.status_code == 200
    assert b"Mentorship workspace" in learner_view.data
    assert b"Mohamed Kamara" in learner_view.data
    assert b"Add progress update" in learner_view.data
    assert b"Provide feedback" not in learner_view.data

    client.post("/auth/logout")
    login(client, mentor.email)
    mentor_view = client.get(f"/mentorship/{mentorship.id}/workspace")
    assert mentor_view.status_code == 200
    assert b"Mariama Conteh" in mentor_view.data
    assert b"Provide feedback" in mentor_view.data
    assert b"Add progress update" not in mentor_view.data


@pytest.mark.parametrize("role_name", ("freelancer", "mentor", "client", "administrator"))
def test_workspace_02_unrelated_users_are_denied(
    client, user_factory, workspace_relationship, role_name
):
    mentorship, _, _ = workspace_relationship
    outsider = user_factory(email=f"outside-{role_name}@example.com", role_name=role_name)
    login(client, outsider.email)
    assert client.get(f"/mentorship/{mentorship.id}/workspace").status_code == 403
    assert client.post(f"/mentorship/{mentorship.id}/goals", data={}).status_code == 403


def test_workspace_03_inactive_relationship_has_no_workspace(
    client, workspace_relationship
):
    mentorship, learner, _ = workspace_relationship
    mentorship.status = "inactive"
    db.session.commit()
    login(client, learner.email)
    assert client.get(f"/mentorship/{mentorship.id}/workspace").status_code == 404


@pytest.mark.parametrize("actor", ("learner", "mentor"))
def test_workspace_04_both_participants_create_goals_and_notify_the_other(
    client, workspace_relationship, actor
):
    mentorship, learner, mentor = workspace_relationship
    author = learner if actor == "learner" else mentor
    recipient = mentor if actor == "learner" else learner
    login(client, author.email)
    response = client.post(
        f"/mentorship/{mentorship.id}/goals",
        data={
            "goal-title": "Build a responsive portfolio website",
            "goal-description": "Publish a responsive portfolio with three professional projects.",
        },
        follow_redirects=True,
    )
    goal = db.session.scalar(db.select(MentorshipGoal))
    notification = db.session.scalar(
        db.select(Notification).where(Notification.user_id == recipient.id)
    )
    assert response.status_code == 200
    assert goal.mentorship_id == mentorship.id
    assert goal.status == "active"
    assert "Build a responsive portfolio website" in notification.message


def test_workspace_05_empty_goal_is_rejected(client, workspace_relationship):
    mentorship, learner, _ = workspace_relationship
    login(client, learner.email)
    response = client.post(
        f"/mentorship/{mentorship.id}/goals",
        data={"goal-title": "", "goal-description": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert db.session.scalar(db.select(MentorshipGoal)) is None
    assert b"This field is required" in response.data


def test_workspace_06_participant_completes_own_relationship_goal_only(
    client, user_factory, workspace_relationship
):
    mentorship, learner, mentor = workspace_relationship
    other_mentor = user_factory(email="other-mentor@example.com", role_name="mentor")
    other_relationship = Mentorship(freelancer=learner, mentor=other_mentor)
    own_goal = MentorshipGoal(
        mentorship=mentorship, title="Own goal", description="A valid own goal description."
    )
    other_goal = MentorshipGoal(
        mentorship=other_relationship,
        title="Other goal",
        description="A valid other goal description.",
    )
    db.session.add_all([other_relationship, own_goal, other_goal])
    db.session.commit()
    login(client, learner.email)

    assert client.post(
        f"/mentorship/{mentorship.id}/goals/{other_goal.id}/complete"
    ).status_code == 403
    response = client.post(
        f"/mentorship/{mentorship.id}/goals/{own_goal.id}/complete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert own_goal.status == "completed"
    assert own_goal.completed_at is not None
    assert db.session.scalar(
        db.select(Notification).where(Notification.user_id == mentor.id)
    ) is not None


def test_workspace_07_only_mentee_posts_progress_and_notifies_mentor(
    client, workspace_relationship
):
    mentorship, learner, mentor = workspace_relationship
    goal = MentorshipGoal(
        mentorship=mentorship,
        title="Portfolio",
        description="Build and publish a professional portfolio website.",
    )
    db.session.add(goal)
    db.session.commit()

    login(client, mentor.email)
    assert client.post(
        f"/mentorship/{mentorship.id}/progress",
        data={"progress-goal_id": goal.id, "progress-content": "Mentor cannot post this."},
    ).status_code == 403
    client.post("/auth/logout")
    login(client, learner.email)
    response = client.post(
        f"/mentorship/{mentorship.id}/progress",
        data={
            "progress-goal_id": goal.id,
            "progress-content": "I completed the HTML and CSS structure and started mobile testing.",
        },
        follow_redirects=True,
    )
    update = db.session.scalar(db.select(MentorshipProgressUpdate))
    assert response.status_code == 200
    assert update.author_id == learner.id
    assert update.goal_id == goal.id
    assert db.session.scalar(
        db.select(Notification).where(
            Notification.user_id == mentor.id,
            Notification.notification_type == "mentorship_progress",
        )
    ) is not None


def test_workspace_08_progress_rejects_empty_and_cross_workspace_goal(
    client, user_factory, workspace_relationship
):
    mentorship, learner, _ = workspace_relationship
    other_mentor = user_factory(email="mentor-two@example.com", role_name="mentor")
    other_relationship = Mentorship(freelancer=learner, mentor=other_mentor)
    other_goal = MentorshipGoal(
        mentorship=other_relationship,
        title="Unrelated goal",
        description="This goal belongs to a separate mentorship.",
    )
    db.session.add_all([other_relationship, other_goal])
    db.session.commit()
    login(client, learner.email)

    client.post(
        f"/mentorship/{mentorship.id}/progress",
        data={"progress-goal_id": 0, "progress-content": ""},
    )
    client.post(
        f"/mentorship/{mentorship.id}/progress",
        data={
            "progress-goal_id": other_goal.id,
            "progress-content": "This update must not attach across workspaces.",
        },
    )
    assert db.session.scalar(db.select(MentorshipProgressUpdate)) is None


def test_workspace_09_only_assigned_mentor_provides_feedback(
    client, user_factory, workspace_relationship
):
    mentorship, learner, mentor = workspace_relationship
    update = MentorshipProgressUpdate(
        mentorship=mentorship,
        author=learner,
        content="I completed the responsive homepage structure this week.",
    )
    db.session.add(update)
    db.session.commit()

    login(client, learner.email)
    assert client.post(
        f"/mentorship/{mentorship.id}/feedback",
        data={"feedback-content": "Learners cannot create mentor feedback."},
    ).status_code == 403
    client.post("/auth/logout")
    outsider = user_factory(email="outside-mentor@example.com", role_name="mentor")
    login(client, outsider.email)
    assert client.post(
        f"/mentorship/{mentorship.id}/feedback",
        data={"feedback-content": "An unrelated mentor cannot add feedback."},
    ).status_code == 403
    client.post("/auth/logout")
    login(client, mentor.email)
    response = client.post(
        f"/mentorship/{mentorship.id}/feedback",
        data={
            "feedback-progress_update_id": update.id,
            "feedback-goal_id": 0,
            "feedback-content": "Good progress. Test the mobile navigation at 375px and 768px next.",
        },
        follow_redirects=True,
    )
    feedback = db.session.scalar(db.select(MentorshipFeedback))
    assert response.status_code == 200
    assert feedback.mentor_id == mentor.id
    assert feedback.progress_update_id == update.id
    assert db.session.scalar(
        db.select(Notification).where(
            Notification.user_id == learner.id,
            Notification.notification_type == "mentorship_feedback",
        )
    ) is not None


def test_workspace_10_feedback_rejects_cross_workspace_update(
    client, user_factory, workspace_relationship
):
    mentorship, learner, mentor = workspace_relationship
    other_learner = user_factory(email="other-learner@example.com")
    other_relationship = Mentorship(freelancer=other_learner, mentor=mentor)
    other_update = MentorshipProgressUpdate(
        mentorship=other_relationship,
        author=other_learner,
        content="This update belongs to another mentorship workspace.",
    )
    db.session.add_all([other_relationship, other_update])
    db.session.commit()
    login(client, mentor.email)
    client.post(
        f"/mentorship/{mentorship.id}/feedback",
        data={
            "feedback-progress_update_id": other_update.id,
            "feedback-goal_id": 0,
            "feedback-content": "This feedback must not attach across workspaces.",
        },
    )
    assert db.session.scalar(db.select(MentorshipFeedback)) is None


def test_workspace_11_content_is_escaped_and_forms_are_csrf_ready(
    client, workspace_relationship
):
    mentorship, learner, _ = workspace_relationship
    db.session.add(
        MentorshipGoal(
            mentorship=mentorship,
            title="<script>alert(1)</script>",
            description="A sufficiently long <img src=x onerror=alert(1)> description.",
        )
    )
    db.session.commit()
    login(client, learner.email)
    response = client.get(f"/mentorship/{mentorship.id}/workspace")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data
    assert response.data.count(b'name="csrf_token"') >= 2
    assert client.get(f"/mentorship/{mentorship.id}/goals").status_code == 405


def test_workspace_12_csrf_blocks_state_change_when_enabled(
    app, client, workspace_relationship
):
    mentorship, learner, _ = workspace_relationship
    login(client, learner.email)
    app.config["WTF_CSRF_ENABLED"] = True
    response = client.post(
        f"/mentorship/{mentorship.id}/goals",
        data={
            "goal-title": "Blocked goal",
            "goal-description": "This request has no CSRF token and must be blocked.",
        },
    )
    assert response.status_code == 400
    assert db.session.scalar(db.select(MentorshipGoal)) is None


def test_workspace_13_dashboards_and_relationship_views_link_to_workspace(
    client, workspace_relationship
):
    mentorship, learner, mentor = workspace_relationship
    login(client, learner.email)
    for path in ("/users/dashboard", "/mentorship/requests/mine"):
        response = client.get(path)
        assert f"/mentorship/{mentorship.id}/workspace".encode() in response.data
        assert b"Open Workspace" in response.data
    client.post("/auth/logout")
    login(client, mentor.email)
    for path in ("/users/dashboard", "/mentorship/mentees"):
        response = client.get(path)
        assert f"/mentorship/{mentorship.id}/workspace".encode() in response.data
        assert b"Open Workspace" in response.data
