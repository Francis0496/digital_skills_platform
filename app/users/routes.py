from pathlib import Path
from uuid import uuid4

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError

from app.auth.decorators import roles_required
from app.extensions import db
from app.models import MentorProfile, Skill, User, UserSkill
from . import bp
from .forms import ConfirmForm, MentorProfileForm, ProfileForm, SkillForm


DASHBOARD_CONTENT = {
    "freelancer": {
        "eyebrow": "Freelancer workspace",
        "title": "Build your digital career",
        "description": "Your learning, portfolio, applications, and mentorship activity will come together here as each module is released.",
        "next_title": "Complete your professional profile",
        "next_text": "Add your background and digital skills to prepare for later learning and marketplace features.",
    },
    "mentor": {
        "eyebrow": "Mentor workspace",
        "title": "Support emerging digital talent",
        "description": "Mentorship requests and active mentee information will appear here when the mentorship module is available.",
        "next_title": "Complete your mentor profile",
        "next_text": "Add your professional title, expertise, experience, and availability.",
    },
    "client": {
        "eyebrow": "Client workspace",
        "title": "Connect with skilled freelancers",
        "description": "Your opportunities and applicant activity will appear here when the marketplace modules are released.",
        "next_title": "Complete your client profile",
        "next_text": "Add your contact, location, and organisation background to prepare for Increment 6.",
    },
    "administrator": {
        "eyebrow": "Administration workspace",
        "title": "Manage the platform",
        "description": "Platform statistics and management tools will appear here when the administration module is released.",
        "next_title": "Authentication is ready",
        "next_text": "Administrative management tools remain scheduled for Increment 9.",
    },
}


@bp.get("/dashboard")
@login_required
def dashboard():
    return render_template(
        "users/dashboard.html", dashboard=DASHBOARD_CONTENT[current_user.role_name]
    )


@bp.get("/profile")
@login_required
def profile():
    return render_template("users/profile.html")


@bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        duplicate = db.session.scalar(
            db.select(User).where(User.email == email, User.id != current_user.id)
        )
        if duplicate:
            form.email.errors.append("An account already uses this email address.")
        else:
            new_image = None
            if form.profile_image.data:
                try:
                    new_image = _save_profile_image(form.profile_image.data)
                except (
                    UnidentifiedImageError,
                    OSError,
                    ValueError,
                    Image.DecompressionBombError,
                ):
                    form.profile_image.errors.append(
                        "The uploaded file is not a valid JPG, PNG, or WebP image."
                    )

            if not form.profile_image.errors:
                old_image = current_user.profile_image
                current_user.full_name = form.full_name.data.strip()
                current_user.email = email
                current_user.phone = _clean_optional(form.phone.data)
                current_user.location = _clean_optional(form.location.data)
                current_user.bio = _clean_optional(form.bio.data)
                if new_image:
                    current_user.profile_image = new_image
                db.session.commit()
                if new_image and old_image:
                    _remove_profile_image(old_image)
                flash("Your profile has been updated.", "success")
                return redirect(url_for("users.profile"))

    return render_template("users/edit_profile.html", form=form)


@bp.get("/profile-image/<path:filename>")
@login_required
def profile_image(filename):
    if filename != current_user.profile_image:
        abort(404)
    return send_from_directory(current_app.config["PROFILE_UPLOAD_FOLDER"], filename)


@bp.route("/skills", methods=["GET", "POST"])
@roles_required("freelancer")
def skills():
    form = SkillForm()
    available_skills = db.session.scalars(db.select(Skill).order_by(Skill.name)).all()
    form.skill_id.choices = [(skill.id, skill.name) for skill in available_skills]

    if form.validate_on_submit():
        duplicate = db.session.scalar(
            db.select(UserSkill).filter_by(
                user_id=current_user.id, skill_id=form.skill_id.data
            )
        )
        if duplicate:
            form.skill_id.errors.append("You have already added this skill.")
        else:
            db.session.add(
                UserSkill(
                    user_id=current_user.id,
                    skill_id=form.skill_id.data,
                    proficiency_level=form.proficiency_level.data,
                )
            )
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.skill_id.errors.append("You have already added this skill.")
            else:
                flash("Skill added to your profile.", "success")
                return redirect(url_for("users.skills"))

    user_skills = db.session.scalars(
        db.select(UserSkill)
        .where(UserSkill.user_id == current_user.id)
        .join(UserSkill.skill)
        .order_by(Skill.name)
    ).all()
    return render_template(
        "users/skills.html", form=form, user_skills=user_skills, remove_form=ConfirmForm()
    )


@bp.post("/skills/<int:user_skill_id>/remove")
@roles_required("freelancer")
def remove_skill(user_skill_id):
    form = ConfirmForm()
    if not form.validate_on_submit():
        abort(400)
    user_skill = db.get_or_404(UserSkill, user_skill_id)
    if user_skill.user_id != current_user.id:
        abort(403)
    db.session.delete(user_skill)
    db.session.commit()
    flash("Skill removed from your profile.", "success")
    return redirect(url_for("users.skills"))


@bp.route("/mentor-profile/edit", methods=["GET", "POST"])
@roles_required("mentor")
def edit_mentor_profile():
    mentor_profile = current_user.mentor_profile
    form = MentorProfileForm(obj=mentor_profile)
    if form.validate_on_submit():
        if mentor_profile is None:
            mentor_profile = MentorProfile(user=current_user)
            db.session.add(mentor_profile)
        mentor_profile.professional_title = _clean_optional(form.professional_title.data)
        mentor_profile.expertise = _clean_optional(form.expertise.data)
        mentor_profile.experience = _clean_optional(form.experience.data)
        mentor_profile.availability = _clean_optional(form.availability.data)
        db.session.commit()
        flash("Your mentor profile has been updated.", "success")
        return redirect(url_for("users.profile"))
    return render_template("users/edit_mentor_profile.html", form=form)


def _clean_optional(value):
    value = value.strip() if value else ""
    return value or None


def _save_profile_image(upload):
    upload.stream.seek(0)
    with Image.open(upload.stream) as image:
        if image.format not in {"JPEG", "PNG", "WEBP"}:
            raise ValueError("Unsupported image format")
        image.verify()

    upload.stream.seek(0)
    with Image.open(upload.stream) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((800, 800))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        filename = f"{uuid4().hex}.webp"
        destination = Path(current_app.config["PROFILE_UPLOAD_FOLDER"], filename)
        image.save(destination, "WEBP", quality=82, method=6)
    return filename


def _remove_profile_image(filename):
    upload_root = Path(current_app.config["PROFILE_UPLOAD_FOLDER"]).resolve()
    target = Path(upload_root, filename).resolve()
    if target.parent == upload_root and target.is_file():
        target.unlink()
