import pytest
from app.extensions import db
from app.models import MentorProfile, Mentorship, MentorshipRequest

def login(client,email="learner@example.com"):
    return client.post("/auth/login",data={"email":email,"password":"SecurePass123!"},follow_redirects=True)
@pytest.fixture()
def mentor(user_factory):
    user=user_factory(email="mentor@example.com",role_name="mentor"); user.full_name="Primary Mentor"; db.session.add(MentorProfile(user=user,professional_title="Software Engineer",expertise="Web development")); db.session.commit(); return user

def test_mentor_01_directory_and_profile_public(client,mentor):
    response=client.get("/mentorship/mentors"); assert b"Software Engineer" in response.data; assert client.get(f"/mentorship/mentors/{mentor.id}").status_code==200

def test_mentor_02_inactive_mentor_hidden(client,mentor):
    mentor.is_active=False; db.session.commit(); assert b"Primary Mentor" not in client.get("/mentorship/mentors").data; assert client.get(f"/mentorship/mentors/{mentor.id}").status_code==404

def test_mentor_03_freelancer_requests_once(client,user_factory,mentor):
    user=user_factory(); login(client); response=client.post(f"/mentorship/mentors/{mentor.id}/request",data={"message":"Please guide my web development career."},follow_redirects=True); assert b"request sent" in response.data; assert db.session.scalar(db.select(MentorshipRequest).filter_by(freelancer_id=user.id)) is not None
    response=client.get(f"/mentorship/mentors/{mentor.id}/request",follow_redirects=True); assert b"already have a pending request" in response.data

@pytest.mark.parametrize("role",("mentor","client","administrator"))
def test_mentor_04_only_freelancers_request(client,user_factory,mentor,role):
    user_factory(role_name=role); login(client); assert client.get(f"/mentorship/mentors/{mentor.id}/request").status_code==403

def test_mentor_05_recipient_accepts_and_creates_relationship(client,user_factory,mentor):
    freelancer=user_factory(); request=MentorshipRequest(freelancer=freelancer,mentor=mentor,message="Guide me"); db.session.add(request); db.session.commit(); login(client,"mentor@example.com"); response=client.post(f"/mentorship/requests/{request.id}/respond",data={"decision":"accepted"},follow_redirects=True); assert b"accepted" in response.data; assert request.status=="accepted"; assert db.session.scalar(db.select(Mentorship).filter_by(freelancer_id=freelancer.id,mentor_id=mentor.id)) is not None

def test_mentor_06_recipient_rejects_without_relationship(client,user_factory,mentor):
    freelancer=user_factory(); request=MentorshipRequest(freelancer=freelancer,mentor=mentor); db.session.add(request); db.session.commit(); login(client,"mentor@example.com"); client.post(f"/mentorship/requests/{request.id}/respond",data={"decision":"rejected"}); assert request.status=="rejected"; assert db.session.scalar(db.select(Mentorship)) is None

def test_mentor_07_wrong_mentor_cannot_respond(client,user_factory,mentor):
    freelancer=user_factory(); other=user_factory(email="othermentor@example.com",role_name="mentor"); request=MentorshipRequest(freelancer=freelancer,mentor=mentor); db.session.add(request); db.session.commit(); login(client,"othermentor@example.com"); assert client.post(f"/mentorship/requests/{request.id}/respond",data={"decision":"accepted"}).status_code==403

def test_mentor_08_cannot_respond_twice(client,user_factory,mentor):
    freelancer=user_factory(); request=MentorshipRequest(freelancer=freelancer,mentor=mentor,status="rejected"); db.session.add(request); db.session.commit(); login(client,"mentor@example.com"); assert client.post(f"/mentorship/requests/{request.id}/respond",data={"decision":"accepted"}).status_code==409

def test_mentor_09_active_relationship_prevents_new_request(client,user_factory,mentor):
    freelancer=user_factory(); db.session.add(Mentorship(freelancer=freelancer,mentor=mentor)); db.session.commit(); login(client); response=client.get(f"/mentorship/mentors/{mentor.id}/request",follow_redirects=True); assert b"active mentorship" in response.data

def test_mentor_10_mentor_sees_only_own_mentees(client,user_factory,mentor):
    freelancer=user_factory(); freelancer.full_name="Learner One"; other=user_factory(email="othermentor@example.com",role_name="mentor"); other.full_name="Other Mentor"; db.session.add_all([Mentorship(freelancer=freelancer,mentor=mentor),Mentorship(freelancer=freelancer,mentor=other)]); db.session.commit(); login(client,"mentor@example.com"); response=client.get("/mentorship/mentees"); assert response.status_code==200; assert b"Learner One" in response.data; assert b"Other Mentor" not in response.data
