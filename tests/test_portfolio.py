from io import BytesIO
from pathlib import Path
import pytest
from PIL import Image
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Portfolio, PortfolioProject

def login(client, email="learner@example.com"):
    return client.post("/auth/login", data={"email": email, "password": "SecurePass123!"}, follow_redirects=True)
def image_upload():
    stream=BytesIO(); Image.new("RGB", (40,30), "blue").save(stream,"PNG"); stream.seek(0); return stream,"work.png"

def test_portfolio_01_freelancer_creates_portfolio(client,user_factory):
    user=user_factory(); login(client); response=client.post("/portfolio/edit",data={"title":"Web Developer","description":"My work"},follow_redirects=True)
    assert b"Portfolio updated" in response.data; assert db.session.scalar(db.select(Portfolio).filter_by(user_id=user.id)).title=="Web Developer"

@pytest.mark.parametrize("role",("mentor","client","administrator"))
def test_portfolio_02_non_freelancers_forbidden(client,user_factory,role):
    user_factory(role_name=role); login(client); assert client.get("/portfolio/").status_code==403

def test_portfolio_03_one_portfolio_per_user(app,user_factory):
    user=user_factory(); db.session.add_all([Portfolio(user_id=user.id),Portfolio(user_id=user.id)])
    with pytest.raises(IntegrityError): db.session.commit()
    db.session.rollback()

def test_portfolio_04_project_crud_and_image(client,user_factory,app):
    user=user_factory(); portfolio=Portfolio(user=user,title="Designer"); db.session.add(portfolio); db.session.commit(); login(client)
    response=client.post("/portfolio/projects/new",data={"title":"Brand Project","description":"Identity work","project_url":"https://example.com","project_image":image_upload()},content_type="multipart/form-data",follow_redirects=True)
    project=db.session.scalar(db.select(PortfolioProject)); assert b"Project saved" in response.data; assert project.project_image.endswith(".webp"); assert Path(app.config["PROJECT_UPLOAD_FOLDER"],project.project_image).is_file()
    response=client.post(f"/portfolio/projects/{project.id}/delete",follow_redirects=True); assert b"Project deleted" in response.data; assert db.session.get(PortfolioProject,project.id) is None

def test_portfolio_05_owner_controls_hidden_publicly(client,user_factory):
    user=user_factory(); portfolio=Portfolio(user=user,title="Developer"); db.session.add(portfolio); db.session.commit()
    response=client.get(f"/portfolio/{user.id}"); assert response.status_code==200; assert b"Edit portfolio" not in response.data

def test_portfolio_06_cannot_edit_or_delete_another_project(client,user_factory):
    user_factory(); other=user_factory(email="other@example.com"); project=PortfolioProject(portfolio=Portfolio(user=other),title="Other",description="Work"); db.session.add(project); db.session.commit(); login(client)
    assert client.get(f"/portfolio/projects/{project.id}/edit").status_code==403; assert client.post(f"/portfolio/projects/{project.id}/delete").status_code==403

def test_portfolio_07_invalid_image_rejected(client,user_factory):
    user=user_factory(); db.session.add(Portfolio(user=user)); db.session.commit(); login(client)
    response=client.post("/portfolio/projects/new",data={"title":"Bad","description":"Bad image","project_image":(BytesIO(b"fake"),"bad.png")},content_type="multipart/form-data"); assert b"not a valid image" in response.data; assert db.session.scalar(db.select(PortfolioProject)) is None
