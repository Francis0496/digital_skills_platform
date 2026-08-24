from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user
from app.auth.decorators import roles_required
from app.extensions import db
from app.models import MentorProfile, Mentorship, MentorshipRequest, Role, User
from . import bp
from .forms import RequestForm, ResponseForm
from app.notifications.service import notify

@bp.get("/mentors")
def directory():
    mentors=db.session.scalars(db.select(User).join(User.role).where(Role.name=="mentor",User.is_active.is_(True)).order_by(User.full_name)).all()
    return render_template("mentorship/directory.html",mentors=mentors)

@bp.get("/mentors/<int:mentor_id>")
def mentor_detail(mentor_id):
    mentor=db.get_or_404(User,mentor_id)
    if mentor.role_name!="mentor" or not mentor.is_active: abort(404)
    pending=None
    if current_user.is_authenticated and current_user.role_name=="freelancer": pending=db.session.scalar(db.select(MentorshipRequest).filter_by(freelancer_id=current_user.id,mentor_id=mentor.id,status="pending"))
    return render_template("mentorship/mentor_detail.html",mentor=mentor,pending=pending)

@bp.route("/mentors/<int:mentor_id>/request",methods=["GET","POST"])
@roles_required("freelancer")
def request_mentor(mentor_id):
    mentor=db.get_or_404(User,mentor_id)
    if mentor.role_name!="mentor" or not mentor.is_active: abort(404)
    duplicate=db.session.scalar(db.select(MentorshipRequest).filter_by(freelancer_id=current_user.id,mentor_id=mentor.id,status="pending"))
    active=db.session.scalar(db.select(Mentorship).filter_by(freelancer_id=current_user.id,mentor_id=mentor.id,status="active"))
    if duplicate or active:
        flash("You already have a pending request or active mentorship with this mentor.","error"); return redirect(url_for("mentorship.mentor_detail",mentor_id=mentor.id))
    form=RequestForm()
    if form.validate_on_submit():
        db.session.add(MentorshipRequest(freelancer=current_user,mentor=mentor,message=form.message.data.strip() or None)); notify(mentor.id,f"New mentorship request from {current_user.full_name}.","mentorship_request"); db.session.commit(); flash("Mentorship request sent.","success"); return redirect(url_for("mentorship.my_requests"))
    return render_template("mentorship/request_form.html",form=form,mentor=mentor)

@bp.get("/requests/mine")
@roles_required("freelancer")
def my_requests():
    requests=db.session.scalars(db.select(MentorshipRequest).where(MentorshipRequest.freelancer_id==current_user.id).order_by(MentorshipRequest.requested_at.desc())).all()
    active=db.session.scalars(db.select(Mentorship).where(Mentorship.freelancer_id==current_user.id,Mentorship.status=="active")).all()
    return render_template("mentorship/requests.html",requests=requests,active=active,mentor_view=False)

@bp.get("/requests/received")
@roles_required("mentor")
def received_requests():
    requests=db.session.scalars(db.select(MentorshipRequest).where(MentorshipRequest.mentor_id==current_user.id).order_by(MentorshipRequest.requested_at.desc())).all()
    return render_template("mentorship/requests.html",requests=requests,active=[],mentor_view=True,response_form=ResponseForm())

@bp.post("/requests/<int:request_id>/respond")
@roles_required("mentor")
def respond(request_id):
    mentorship_request=db.get_or_404(MentorshipRequest,request_id)
    if mentorship_request.mentor_id!=current_user.id: abort(403)
    if mentorship_request.status!="pending": abort(409)
    form=ResponseForm()
    if not form.validate_on_submit(): abort(400)
    if form.decision.data=="accepted":
        active=db.session.scalar(db.select(Mentorship).filter_by(freelancer_id=mentorship_request.freelancer_id,mentor_id=current_user.id,status="active"))
        if active: abort(409)
        db.session.add(Mentorship(freelancer_id=mentorship_request.freelancer_id,mentor_id=current_user.id))
    mentorship_request.status=form.decision.data; notify(mentorship_request.freelancer_id,f"{current_user.full_name} {form.decision.data} your mentorship request.","mentorship_response"); db.session.commit(); flash(f"Mentorship request {form.decision.data}.","success"); return redirect(url_for("mentorship.received_requests"))

@bp.get("/mentees")
@roles_required("mentor")
def mentees():
    mentorships=db.session.scalars(db.select(Mentorship).where(Mentorship.mentor_id==current_user.id,Mentorship.status=="active")).all()
    return render_template("mentorship/mentees.html",mentorships=mentorships)
