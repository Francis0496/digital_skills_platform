import pytest
from app.extensions import db
from app.models import Course, CourseCategory, FreelanceOpportunity, JobApplication, MentorProfile, MentorshipRequest, Notification, Skill
from app.notifications.service import notify

def login(client,email="learner@example.com"):
    return client.post("/auth/login",data={"email":email,"password":"SecurePass123!"},follow_redirects=True)

def test_notify_01_user_sees_and_reads_own_notifications(client,user_factory):
    user=user_factory(); other=user_factory(email="other@example.com"); notify(user.id,"Your event happened","info"); notify(other.id,"Private event","info"); db.session.commit(); login(client); response=client.get("/notifications/"); assert b"Your event happened" in response.data; assert b"Private event" not in response.data
    item=db.session.scalar(db.select(Notification).filter_by(user_id=user.id)); client.post(f"/notifications/{item.id}/read"); assert item.is_read

def test_notify_02_cannot_read_another_notification(client,user_factory):
    user_factory(); other=user_factory(email="other@example.com"); item=notify(other.id,"Private"); db.session.commit(); login(client); assert client.post(f"/notifications/{item.id}/read").status_code==403

def test_notify_03_mark_all_scoped_to_current_user(client,user_factory):
    user=user_factory(); other=user_factory(email="other@example.com"); notify(user.id,"One"); private=notify(other.id,"Other"); db.session.commit(); login(client); client.post("/notifications/read-all"); assert db.session.scalar(db.select(Notification).filter_by(user_id=user.id)).is_read; assert not private.is_read

def test_notify_04_application_events_create_notifications(client,user_factory):
    freelancer=user_factory(); owner=user_factory(email="client@example.com",role_name="client"); job=FreelanceOpportunity(client=owner,title="Job",description="Work"); db.session.add(job); db.session.commit(); login(client); client.post(f"/applications/opportunities/{job.id}/apply",data={"cover_message":"I have the experience required for this opportunity."}); assert db.session.scalar(db.select(Notification).filter_by(user_id=owner.id,notification_type="application_received"))
    client.post("/auth/logout"); login(client,"client@example.com"); application=db.session.scalar(db.select(JobApplication)); client.post(f"/applications/{application.id}/status",data={"status":"accepted"}); assert db.session.scalar(db.select(Notification).filter_by(user_id=freelancer.id,notification_type="application_status"))

def test_notify_05_mentorship_events_create_notifications(client,user_factory):
    freelancer=user_factory(); mentor=user_factory(email="mentor@example.com",role_name="mentor"); db.session.add(MentorProfile(user=mentor)); db.session.commit(); login(client); client.post(f"/mentorship/mentors/{mentor.id}/request",data={"message":"Please mentor me"}); assert db.session.scalar(db.select(Notification).filter_by(user_id=mentor.id,notification_type="mentorship_request"))
    client.post("/auth/logout"); login(client,"mentor@example.com"); request=db.session.scalar(db.select(MentorshipRequest)); client.post(f"/mentorship/requests/{request.id}/respond",data={"decision":"accepted"}); assert db.session.scalar(db.select(Notification).filter_by(user_id=freelancer.id,notification_type="mentorship_response"))

@pytest.mark.parametrize("role",("freelancer","mentor","client"))
def test_admin_01_non_admin_denied(client,user_factory,role):
    user_factory(role_name=role); login(client)
    for path in ("/admin/","/admin/users","/admin/skills","/admin/mentorships"): assert client.get(path).status_code==403

def test_admin_02_dashboard_statistics(client,user_factory):
    user_factory(role_name="administrator"); user_factory(email="client@example.com",role_name="client"); login(client); response=client.get("/admin/"); assert response.status_code==200; assert b"Platform overview" in response.data; assert b"Total Users" in response.data

def test_admin_03_search_and_toggle_user(client,user_factory):
    admin=user_factory(role_name="administrator"); target=user_factory(email="target@example.com",role_name="client"); login(client); response=client.get("/admin/users?q=target"); assert b"target@example.com" in response.data; client.post(f"/admin/users/{target.id}/toggle-active"); assert not db.session.get(type(target),target.id).is_active; assert client.post(f"/admin/users/{admin.id}/toggle-active").status_code==400

def test_admin_04_skill_create_edit_and_duplicate(client,user_factory):
    user_factory(role_name="administrator"); login(client); client.post("/admin/skills/new",data={"name":"Cybersecurity","description":"Security skills"}); skill=db.session.scalar(db.select(Skill)); assert skill.name=="Cybersecurity"; client.post(f"/admin/skills/{skill.id}/edit",data={"name":"Security","description":"Updated"}); assert skill.name=="Security"; response=client.post("/admin/skills/new",data={"name":"Security"}); assert b"already exists" in response.data

def test_admin_05_mentorship_oversight(client,user_factory):
    user_factory(role_name="administrator"); freelancer=user_factory(email="free@example.com"); mentor=user_factory(email="mentor@example.com",role_name="mentor"); db.session.add(MentorshipRequest(freelancer=freelancer,mentor=mentor)); db.session.commit(); login(client); response=client.get("/admin/mentorships"); assert response.status_code==200; assert b"Mentorship oversight" in response.data

def test_admin_06_workspace_navigation_and_user_table(client,user_factory):
    user_factory(role_name="administrator")
    user_factory(email="client@example.com", role_name="client")
    login(client)
    dashboard = client.get("/admin/")
    assert dashboard.status_code == 200
    for label in (b"Users", b"Skills", b"Learning Content", b"Opportunities", b"Applications", b"Mentorships", b"Notifications"):
        assert label in dashboard.data
    users = client.get("/admin/users")
    assert b'<table class="admin-table">' in users.data
    assert b'name="csrf_token"' in users.data
