from pathlib import Path
from uuid import uuid4
from flask import abort, current_app, flash, redirect, render_template, send_from_directory, url_for
from flask_login import current_user
from PIL import Image, ImageOps, UnidentifiedImageError
from app.auth.decorators import roles_required
from app.extensions import db
from app.matching.service import suggest_skills_for_text
from app.models import Portfolio, PortfolioProject, Skill, User
from . import bp
from .forms import ConfirmForm, PortfolioForm, ProjectForm

@bp.get("/")
@roles_required("freelancer")
def mine():
    portfolio = current_user.portfolio
    return render_template("portfolio/show.html", portfolio=portfolio, owner=True, confirm_form=ConfirmForm())

@bp.get("/<int:user_id>")
def public(user_id):
    user = db.get_or_404(User, user_id)
    if user.role_name != "freelancer" or user.portfolio is None:
        abort(404)
    return render_template("portfolio/show.html", portfolio=user.portfolio, owner=current_user.is_authenticated and current_user.id == user.id, confirm_form=ConfirmForm())

@bp.route("/edit", methods=["GET", "POST"])
@roles_required("freelancer")
def edit():
    portfolio = current_user.portfolio or Portfolio(user=current_user)
    form = PortfolioForm(obj=portfolio)
    if form.validate_on_submit():
        portfolio.title = _clean(form.title.data); portfolio.description = _clean(form.description.data)
        db.session.add(portfolio); db.session.commit(); flash("Portfolio updated.", "success")
        return redirect(url_for("portfolio.mine"))
    return render_template("portfolio/form.html", form=form)

@bp.route("/projects/new", methods=["GET", "POST"])
@roles_required("freelancer")
def create_project():
    if current_user.portfolio is None:
        flash("Create your portfolio introduction before adding projects.", "error")
        return redirect(url_for("portfolio.edit"))
    return _project_form(current_user.portfolio, PortfolioProject())

@bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@roles_required("freelancer")
def edit_project(project_id):
    project = db.get_or_404(PortfolioProject, project_id); _ensure_owner(project)
    return _project_form(project.portfolio, project)

@bp.post("/projects/<int:project_id>/delete")
@roles_required("freelancer")
def delete_project(project_id):
    if not ConfirmForm().validate_on_submit(): abort(400)
    project = db.get_or_404(PortfolioProject, project_id); _ensure_owner(project)
    image = project.project_image; db.session.delete(project); db.session.commit(); _remove_image(image)
    flash("Project deleted.", "success"); return redirect(url_for("portfolio.mine"))

@bp.get("/project-image/<filename>")
def project_image(filename):
    if db.session.scalar(db.select(PortfolioProject).filter_by(project_image=filename)) is None: abort(404)
    return send_from_directory(current_app.config["PROJECT_UPLOAD_FOLDER"], filename)

def _project_form(portfolio, project):
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        new_image = None
        if form.project_image.data:
            try: new_image = _save_image(form.project_image.data)
            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError): form.project_image.errors.append("The uploaded file is not a valid image.")
        if not form.project_image.errors:
            old = project.project_image; project.portfolio = portfolio; project.title = form.title.data.strip(); project.description = form.description.data.strip(); project.project_url = _clean(form.project_url.data); project.completion_date = form.completion_date.data
            if new_image: project.project_image = new_image
            db.session.add(project); db.session.commit()
            if new_image: _remove_image(old)
            flash("Project saved.", "success"); return redirect(url_for("portfolio.mine"))
    description_text = form.description.data or project.description or ""
    available_skills = db.session.scalars(db.select(Skill).order_by(Skill.name)).all()
    have_skill_ids = {user_skill.skill_id for user_skill in current_user.skills}
    suggested_skills = [
        skill
        for skill in suggest_skills_for_text(description_text, known_skills=available_skills)
        if skill.id not in have_skill_ids
    ]
    return render_template(
        "portfolio/project_form.html",
        form=form,
        project=project if project.id else None,
        suggested_skills=suggested_skills,
    )

def _ensure_owner(project):
    if project.portfolio.user_id != current_user.id: abort(403)
def _clean(value):
    return value.strip() or None if value else None
def _save_image(upload):
    upload.stream.seek(0)
    with Image.open(upload.stream) as image:
        if image.format not in {"JPEG", "PNG", "WEBP"}: raise ValueError()
        image.verify()
    upload.stream.seek(0)
    with Image.open(upload.stream) as image:
        image = ImageOps.exif_transpose(image); image.thumbnail((1200, 900))
        if image.mode not in ("RGB", "RGBA"): image = image.convert("RGB")
        filename = f"{uuid4().hex}.webp"; image.save(Path(current_app.config["PROJECT_UPLOAD_FOLDER"], filename), "WEBP", quality=82, method=6)
    return filename
def _remove_image(filename):
    if not filename: return
    root = Path(current_app.config["PROJECT_UPLOAD_FOLDER"]).resolve(); target = Path(root, filename).resolve()
    if target.parent == root and target.is_file(): target.unlink()
