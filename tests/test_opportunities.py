from datetime import date, timedelta
from decimal import Decimal
import pytest
from app.extensions import db
from app.models import FreelanceOpportunity

def login(client,email="learner@example.com"):
    return client.post("/auth/login",data={"email":email,"password":"SecurePass123!"},follow_redirects=True)
def data(**overrides):
    values={"title":"Build a Business Website","description":"Create an accessible website for a local business.","category":"Web Development","budget":"1500.00","deadline":(date.today()+timedelta(days=14)).isoformat()}; values.update(overrides); return values

def test_job_01_client_creates_and_edits_opportunity(client,user_factory):
    user=user_factory(role_name="client"); login(client); response=client.post("/opportunities/new",data=data(),follow_redirects=True); job=db.session.scalar(db.select(FreelanceOpportunity))
    assert b"Opportunity created" in response.data; assert job.client_id==user.id; assert job.budget==Decimal("1500.00"); assert b"SLE 1,500.00" in response.data
    response=client.post(f"/opportunities/{job.id}/edit",data=data(title="Updated Website"),follow_redirects=True); assert b"Opportunity updated" in response.data

@pytest.mark.parametrize("role",("freelancer","mentor"))
def test_job_02_wrong_roles_cannot_create(client,user_factory,role):
    user_factory(role_name=role); login(client); assert client.get("/opportunities/new").status_code==403

def test_job_03_client_cannot_edit_or_close_another_record(client,user_factory):
    user_factory(role_name="client"); other=user_factory(email="other@example.com",role_name="client"); job=FreelanceOpportunity(client=other,title="Other",description="Work"); db.session.add(job); db.session.commit(); login(client)
    assert client.get(f"/opportunities/{job.id}/edit").status_code==403; assert client.post(f"/opportunities/{job.id}/close").status_code==403

def test_job_04_admin_can_manage_any_record(client,user_factory):
    admin=user_factory(role_name="administrator"); owner=user_factory(email="owner@example.com",role_name="client"); job=FreelanceOpportunity(client=owner,title="Job",description="Work"); db.session.add(job); db.session.commit(); login(client)
    assert client.get(f"/opportunities/{job.id}/edit").status_code==200; response=client.post(f"/opportunities/{job.id}/close",follow_redirects=True); assert b"Opportunity closed" in response.data

def test_job_05_catalogue_only_shows_active_unexpired(client,user_factory):
    owner=user_factory(role_name="client"); active=FreelanceOpportunity(client=owner,title="Active Job",description="Open",status="active",deadline=date.today()+timedelta(days=1)); closed=FreelanceOpportunity(client=owner,title="Closed Job",description="Closed",status="closed"); expired=FreelanceOpportunity(client=owner,title="Expired Job",description="Expired",status="active",deadline=date.today()-timedelta(days=1)); db.session.add_all([active,closed,expired]); db.session.commit()
    response=client.get("/opportunities/"); assert b"Active Job" in response.data; assert b"Closed Job" not in response.data; assert b"Expired Job" not in response.data

def test_job_06_search_and_category_filters(client,user_factory):
    owner=user_factory(role_name="client"); db.session.add_all([FreelanceOpportunity(client=owner,title="Logo Design",description="Brand",category="Design"),FreelanceOpportunity(client=owner,title="Python Script",description="Automation",category="Development")]); db.session.commit()
    response=client.get("/opportunities/?q=logo&category=Design"); assert b"Logo Design" in response.data; assert b"Python Script" not in response.data

def test_job_07_past_deadline_and_negative_budget_rejected(client,user_factory):
    user_factory(role_name="client"); login(client); response=client.post("/opportunities/new",data=data(deadline=(date.today()-timedelta(days=1)).isoformat(),budget="-1")); assert b"Deadline cannot be in the past" in response.data; assert db.session.scalar(db.select(FreelanceOpportunity)) is None

def test_job_08_close_changes_lifecycle(client,user_factory):
    owner=user_factory(role_name="client"); job=FreelanceOpportunity(client=owner,title="Job",description="Work"); db.session.add(job); db.session.commit(); login(client); client.post(f"/opportunities/{job.id}/close"); assert db.session.get(FreelanceOpportunity,job.id).status=="closed"; assert not job.accepts_applications

def test_job_09_expired_effective_status(user_factory):
    owner=user_factory(role_name="client"); job=FreelanceOpportunity(client=owner,title="Old",description="Work",deadline=date.today()-timedelta(days=1)); assert job.effective_status=="expired"; assert not job.accepts_applications
