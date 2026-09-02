from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from app.auth.decorators import roles_required
from app.extensions import db
from app.matching.service import compute_application_match
from app.models import FreelanceOpportunity, JobApplication
from . import bp
from .forms import ApplicationForm, StatusForm
from app.notifications.service import notify

@bp.route("/opportunities/<int:opportunity_id>/apply", methods=["GET", "POST"])
@roles_required("freelancer")
def apply(opportunity_id):
    opportunity = db.get_or_404(FreelanceOpportunity, opportunity_id)
    if not opportunity.accepts_applications: abort(403)
    existing = db.session.scalar(db.select(JobApplication).filter_by(opportunity_id=opportunity.id, freelancer_id=current_user.id))
    if existing:
        flash("You have already applied to this opportunity.", "error")
        return redirect(url_for("applications.detail", application_id=existing.id))
    form = ApplicationForm()
    match = compute_application_match(current_user, opportunity, form.cover_message.data or "")
    if form.validate_on_submit():
        application = JobApplication(opportunity=opportunity, freelancer=current_user, cover_message=form.cover_message.data.strip(), proposed_amount=form.proposed_amount.data)
        db.session.add(application)
        notify(opportunity.client_id, f"New application received for {opportunity.title}.", "application_received")
        try: db.session.commit()
        except IntegrityError:
            db.session.rollback(); flash("You have already applied to this opportunity.", "error")
            return redirect(url_for("opportunities.detail", opportunity_id=opportunity.id))
        flash("Application submitted.", "success")
        return redirect(url_for("applications.detail", application_id=application.id))
    return render_template("applications/form.html", form=form, opportunity=opportunity, match=match)

@bp.get("/mine")
@roles_required("freelancer")
def mine():
    applications = db.session.scalars(db.select(JobApplication).where(JobApplication.freelancer_id==current_user.id).order_by(JobApplication.submitted_at.desc())).all()
    return render_template("applications/mine.html", applications=applications)

@bp.get("/opportunities/<int:opportunity_id>")
@roles_required("client", "administrator")
def for_opportunity(opportunity_id):
    opportunity=db.get_or_404(FreelanceOpportunity,opportunity_id); _ensure_reviewer(opportunity)
    return render_template("applications/review_list.html", opportunity=opportunity)

@bp.get("/<int:application_id>")
@roles_required("freelancer", "client", "administrator")
def detail(application_id):
    application=db.get_or_404(JobApplication,application_id); _ensure_viewer(application)
    return render_template("applications/detail.html", application=application, status_form=StatusForm())

@bp.post("/<int:application_id>/status")
@roles_required("client", "administrator")
def update_status(application_id):
    application=db.get_or_404(JobApplication,application_id); _ensure_reviewer(application.opportunity)
    form=StatusForm()
    if not form.validate_on_submit(): abort(400)
    application.status=form.status.data
    notify(application.freelancer_id, f"Your application for {application.opportunity.title} is now {application.status.replace('_',' ')}.", "application_status")
    db.session.commit(); flash("Application status updated.", "success")
    return redirect(url_for("applications.detail",application_id=application.id))

@bp.get("/admin/all")
@roles_required("administrator")
def oversight():
    applications=db.session.scalars(db.select(JobApplication).order_by(JobApplication.submitted_at.desc())).all()
    return render_template("applications/mine.html", applications=applications, oversight=True)

def _ensure_reviewer(opportunity):
    if current_user.role_name!="administrator" and opportunity.client_id!=current_user.id: abort(403)
def _ensure_viewer(application):
    allowed=current_user.role_name=="administrator" or application.freelancer_id==current_user.id or (current_user.role_name=="client" and application.opportunity.client_id==current_user.id)
    if not allowed: abort(403)
