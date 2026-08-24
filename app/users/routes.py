from pathlib import Path
from uuid import uuid4
from datetime import date

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
from app.models import (
    FreelanceOpportunity,
    JobApplication,
    MentorProfile,
    Mentorship,
    MentorshipRequest,
    Notification,
    Skill,
    User,
    UserSkill,
)
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
        "description": "Review mentorship requests, support active mentees, and maintain your professional profile.",
        "next_title": "Complete your mentor profile",
        "next_text": "Add your professional title, expertise, experience, and availability.",
    },
    "client": {
        "eyebrow": "Client workspace",
        "title": "Connect with skilled freelancers",
        "description": "Manage opportunities, review applicants, and monitor marketplace activity.",
        "next_title": "Complete your client profile",
        "next_text": "Keep your contact, location, and organisation background current.",
    },
    "administrator": {
        "eyebrow": "Administration workspace",
        "title": "Manage the platform",
        "description": "Monitor platform activity, manage users, oversee learning content, and review platform operations.",
        "next_title": "Platform operations",
        "next_text": "Use the Administrator workspace to access implemented management tools.",
    },
}


@bp.get("/dashboard")
@login_required
def dashboard():
    if current_user.role_name == "administrator":
        return redirect(url_for("admin.dashboard"))
    context = {"dashboard": DASHBOARD_CONTENT[current_user.role_name]}
    if current_user.role_name == "freelancer":
        enrollments = sorted(
            current_user.enrollments,
            key=lambda item: item.enrolled_at,
            reverse=True,
        )
        applications = db.session.scalars(
            db.select(JobApplication)
            .where(JobApplication.freelancer_id == current_user.id)
            .order_by(JobApplication.submitted_at.desc())
        ).all()
        active_mentorships = db.session.scalar(
            db.select(db.func.count(Mentorship.id)).where(
                Mentorship.freelancer_id == current_user.id,
                Mentorship.status == "active",
            )
        )
        mentorship_requests = db.session.scalar(
            db.select(db.func.count(MentorshipRequest.id)).where(
                MentorshipRequest.freelancer_id == current_user.id,
                MentorshipRequest.status == "pending",
            )
        )
        recent_opportunities = db.session.scalars(
            db.select(FreelanceOpportunity)
            .where(
                FreelanceOpportunity.status == "active",
                db.or_(
                    FreelanceOpportunity.deadline.is_(None),
                    FreelanceOpportunity.deadline >= date.today(),
                ),
            )
            .order_by(FreelanceOpportunity.created_at.desc())
            .limit(3)
        ).all()
        recent_notifications = db.session.scalars(
            db.select(Notification)
            .where(Notification.user_id == current_user.id)
            .order_by(Notification.created_at.desc())
            .limit(4)
        ).all()
        context.update(
            enrollments=enrollments,
            continue_enrollment=next(
                (
                    item
                    for item in enrollments
                    if item.completion_status != "completed" and item.course.lessons
                ),
                None,
            ),
            applications=applications,
            active_application_count=sum(
                item.status in {"pending", "under_review"} for item in applications
            ),
            active_mentorships=active_mentorships,
            mentorship_requests=mentorship_requests,
            recent_opportunities=recent_opportunities,
            recent_notifications=recent_notifications,
            project_count=len(current_user.portfolio.projects)
            if current_user.portfolio
            else 0,
        )
    elif current_user.role_name == "mentor":
        requests = db.session.scalars(
            db.select(MentorshipRequest)
            .where(MentorshipRequest.mentor_id == current_user.id)
            .order_by(MentorshipRequest.requested_at.desc())
        ).all()
        mentorships = db.session.scalars(
            db.select(Mentorship)
            .where(
                Mentorship.mentor_id == current_user.id,
                Mentorship.status == "active",
            )
            .order_by(Mentorship.start_date.desc())
        ).all()
        recent_notifications = db.session.scalars(
            db.select(Notification)
            .where(Notification.user_id == current_user.id)
            .order_by(Notification.created_at.desc())
            .limit(5)
        ).all()
        context.update(
            mentor_requests=requests,
            pending_request_count=sum(item.status == "pending" for item in requests),
            accepted_request_count=sum(item.status == "accepted" for item in requests),
            active_mentorships=mentorships,
            recent_notifications=recent_notifications,
            unread_notification_count=sum(not item.is_read for item in recent_notifications),
            mentor_profile=current_user.mentor_profile,
        )
    elif current_user.role_name == "client":
        opportunities = db.session.scalars(
            db.select(FreelanceOpportunity)
            .where(FreelanceOpportunity.client_id == current_user.id)
            .order_by(FreelanceOpportunity.created_at.desc())
        ).all()
        opportunity_ids = [item.id for item in opportunities]
        applications = (
            db.session.scalars(
                db.select(JobApplication)
                .where(JobApplication.opportunity_id.in_(opportunity_ids))
                .order_by(JobApplication.submitted_at.desc())
            ).all()
            if opportunity_ids
            else []
        )
        recent_notifications = db.session.scalars(
            db.select(Notification)
            .where(Notification.user_id == current_user.id)
            .order_by(Notification.created_at.desc())
            .limit(5)
        ).all()
        context.update(
            client_opportunities=opportunities,
            client_applications=applications,
            active_opportunity_count=sum(item.effective_status == "active" for item in opportunities),
            closed_opportunity_count=sum(item.effective_status == "closed" for item in opportunities),
            pending_review_count=sum(item.status in {"pending", "under_review"} for item in applications),
            recent_notifications=recent_notifications,
        )
    return render_template("users/dashboard.html", **context)


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


@bp.get("/avatar/<int:user_id>")
def avatar_image(user_id):
    """Serve an account avatar without exposing its stored filename in page markup."""
    user = db.session.get(User, user_id)
    if user is None or not user.is_active or not user.profile_image:
        abort(404)
    if not current_user.is_authenticated and user.role_name != "mentor":
        abort(404)
    return send_from_directory(
        current_app.config["PROFILE_UPLOAD_FOLDER"], user.profile_image
    )


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
