from datetime import date, timedelta
from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import FreelanceOpportunity, JobApplication

def login(client,email="learner@example.com"):
    return client.post("/auth/login",data={"email":email,"password":"SecurePass123!"},follow_redirects=True)
@pytest.fixture()
def opportunity(user_factory):
    owner=user_factory(email="client@example.com",role_name="client"); item=FreelanceOpportunity(client=owner,title="Website Project",description="Build website",deadline=date.today()+timedelta(days=5)); db.session.add(item); db.session.commit(); return item
def apply_data(**overrides):
    values={"cover_message":"I have relevant experience and can deliver this project successfully.","proposed_amount":"500.00"}; values.update(overrides); return values

def test_app_01_freelancer_submits_and_tracks(client,user_factory,opportunity):
    user=user_factory(); login(client); response=client.post(f"/applications/opportunities/{opportunity.id}/apply",data=apply_data(),follow_redirects=True); record=db.session.scalar(db.select(JobApplication))
    assert b"Application submitted" in response.data; assert record.freelancer_id==user.id; assert record.proposed_amount==Decimal("500.00"); assert b"Pending" in client.get("/applications/mine").data

def test_app_02_duplicate_application_rejected(client,user_factory,opportunity):
    user=user_factory(); db.session.add(JobApplication(opportunity=opportunity,freelancer=user,cover_message="Existing application message")); db.session.commit(); login(client); response=client.get(f"/applications/opportunities/{opportunity.id}/apply",follow_redirects=True); assert b"already applied" in response.data; assert db.session.scalar(db.select(db.func.count(JobApplication.id)))==1

@pytest.mark.parametrize("status",("closed","expired"))
def test_app_03_closed_or_expired_rejected(client,user_factory,opportunity,status):
    user_factory(); opportunity.status="closed" if status=="closed" else "active"; opportunity.deadline=date.today()-timedelta(days=1) if status=="expired" else opportunity.deadline; db.session.commit(); login(client); assert client.get(f"/applications/opportunities/{opportunity.id}/apply").status_code==403

@pytest.mark.parametrize("role",("mentor","client","administrator"))
def test_app_04_only_freelancers_apply(client,user_factory,opportunity,role):
    user_factory(role_name=role); login(client); assert client.get(f"/applications/opportunities/{opportunity.id}/apply").status_code==403

def test_app_05_owner_client_reviews_and_updates(client,user_factory,opportunity):
    freelancer=user_factory(); record=JobApplication(opportunity=opportunity,freelancer=freelancer,cover_message="Strong application message"); db.session.add(record); db.session.commit(); login(client,"client@example.com"); assert client.get(f"/applications/opportunities/{opportunity.id}").status_code==200; response=client.post(f"/applications/{record.id}/status",data={"status":"under_review"},follow_redirects=True); assert b"status updated" in response.data; assert db.session.get(JobApplication,record.id).status=="under_review"

def test_app_06_other_client_cannot_review(client,user_factory,opportunity):
    freelancer=user_factory(); other=user_factory(email="otherclient@example.com",role_name="client"); record=JobApplication(opportunity=opportunity,freelancer=freelancer,cover_message="Strong application message"); db.session.add(record); db.session.commit(); login(client,"otherclient@example.com"); assert client.get(f"/applications/{record.id}").status_code==403; assert client.post(f"/applications/{record.id}/status",data={"status":"accepted"}).status_code==403

def test_app_07_freelancer_cannot_view_another_application(client,user_factory,opportunity):
    user_factory(); other=user_factory(email="other@example.com"); record=JobApplication(opportunity=opportunity,freelancer=other,cover_message="Strong application message"); db.session.add(record); db.session.commit(); login(client); assert client.get(f"/applications/{record.id}").status_code==403

def test_app_08_invalid_status_rejected(client,user_factory,opportunity):
    freelancer=user_factory(); record=JobApplication(opportunity=opportunity,freelancer=freelancer,cover_message="Strong application message"); db.session.add(record); db.session.commit(); login(client,"client@example.com"); assert client.post(f"/applications/{record.id}/status",data={"status":"withdrawn"}).status_code==400

def test_app_09_database_prevents_duplicates(user_factory,opportunity):
    user=user_factory(); db.session.add_all([JobApplication(opportunity=opportunity,freelancer=user,cover_message="First valid message"),JobApplication(opportunity=opportunity,freelancer=user,cover_message="Second valid message")]);
    with pytest.raises(IntegrityError): db.session.commit()
    db.session.rollback()

def test_app_10_admin_oversight(client,user_factory,opportunity):
    admin=user_factory(role_name="administrator"); freelancer=user_factory(email="freelancer@example.com"); db.session.add(JobApplication(opportunity=opportunity,freelancer=freelancer,cover_message="Strong application message")); db.session.commit(); login(client); response=client.get("/applications/admin/all"); assert response.status_code==200; assert b"Application oversight" in response.data
