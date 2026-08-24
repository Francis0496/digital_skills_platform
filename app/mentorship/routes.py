from datetime import datetime, timezone

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload

from app.auth.decorators import roles_required
from app.extensions import db
from app.models import (
    MentorProfile,
    Mentorship,
    MentorshipFeedback,
    MentorshipGoal,
    MentorshipProgressUpdate,
    MentorshipRequest,
    Role,
    User,
)
from app.notifications.service import notify

from . import bp
from .forms import (
    FeedbackForm,
    GoalForm,
    ProgressUpdateForm,
    RequestForm,
    ResponseForm,
    WorkspaceActionForm,
)


def _active_participant(mentorship_id):
    mentorship = db.session.scalar(
        db.select(Mentorship)
        .where(Mentorship.id == mentorship_id)
        .options(
            selectinload(Mentorship.goals),
            selectinload(Mentorship.progress_updates).selectinload(
                MentorshipProgressUpdate.goal
            ),
            selectinload(Mentorship.progress_updates).selectinload(
                MentorshipProgressUpdate.feedback_entries
            ),
            selectinload(Mentorship.feedback_entries).selectinload(
                MentorshipFeedback.goal
            ),
        )
    )
    if mentorship is None or mentorship.status != "active":
        abort(404)
    if current_user.id not in (mentorship.freelancer_id, mentorship.mentor_id):
        abort(403)
    return mentorship


def _other_participant(mentorship):
    return (
        mentorship.mentor
        if current_user.id == mentorship.freelancer_id
        else mentorship.freelancer
    )


def _goal_choices(mentorship):
    return [(0, "General mentorship progress")] + [
        (goal.id, goal.title) for goal in mentorship.goals
    ]


def _progress_choices(mentorship):
    updates = sorted(
        mentorship.progress_updates, key=lambda item: item.created_at, reverse=True
    )
    return [(0, "General feedback")] + [
        (item.id, f"{item.created_at.strftime('%d %b')}: {item.content[:70]}")
        for item in updates
    ]


def _form_error(form, default):
    first_error = next(
        (message for messages in form.errors.values() for message in messages), default
    )
    flash(first_error, "error")


@bp.get("/mentors")
def directory():
    mentors = db.session.scalars(
        db.select(User)
        .join(User.role)
        .where(Role.name == "mentor", User.is_active.is_(True))
        .order_by(User.full_name)
    ).all()
    return render_template("mentorship/directory.html", mentors=mentors)


@bp.get("/mentors/<int:mentor_id>")
def mentor_detail(mentor_id):
    mentor = db.get_or_404(User, mentor_id)
    if mentor.role_name != "mentor" or not mentor.is_active:
        abort(404)
    pending = None
    if current_user.is_authenticated and current_user.role_name == "freelancer":
        pending = db.session.scalar(
            db.select(MentorshipRequest).filter_by(
                freelancer_id=current_user.id, mentor_id=mentor.id, status="pending"
            )
        )
    return render_template("mentorship/mentor_detail.html", mentor=mentor, pending=pending)


@bp.route("/mentors/<int:mentor_id>/request", methods=["GET", "POST"])
@roles_required("freelancer")
def request_mentor(mentor_id):
    mentor = db.get_or_404(User, mentor_id)
    if mentor.role_name != "mentor" or not mentor.is_active:
        abort(404)
    duplicate = db.session.scalar(
        db.select(MentorshipRequest).filter_by(
            freelancer_id=current_user.id, mentor_id=mentor.id, status="pending"
        )
    )
    active = db.session.scalar(
        db.select(Mentorship).filter_by(
            freelancer_id=current_user.id, mentor_id=mentor.id, status="active"
        )
    )
    if duplicate or active:
        flash(
            "You already have a pending request or active mentorship with this mentor.",
            "error",
        )
        return redirect(url_for("mentorship.mentor_detail", mentor_id=mentor.id))
    form = RequestForm()
    if form.validate_on_submit():
        db.session.add(
            MentorshipRequest(
                freelancer=current_user,
                mentor=mentor,
                message=form.message.data.strip() or None,
            )
        )
        notify(
            mentor.id,
            f"New mentorship request from {current_user.full_name}.",
            "mentorship_request",
        )
        db.session.commit()
        flash("Mentorship request sent.", "success")
        return redirect(url_for("mentorship.my_requests"))
    return render_template("mentorship/request_form.html", form=form, mentor=mentor)


@bp.get("/requests/mine")
@roles_required("freelancer")
def my_requests():
    requests = db.session.scalars(
        db.select(MentorshipRequest)
        .where(MentorshipRequest.freelancer_id == current_user.id)
        .order_by(MentorshipRequest.requested_at.desc())
    ).all()
    active = db.session.scalars(
        db.select(Mentorship).where(
            Mentorship.freelancer_id == current_user.id,
            Mentorship.status == "active",
        )
    ).all()
    return render_template(
        "mentorship/requests.html",
        requests=requests,
        active=active,
        mentor_view=False,
    )


@bp.get("/requests/received")
@roles_required("mentor")
def received_requests():
    requests = db.session.scalars(
        db.select(MentorshipRequest)
        .where(MentorshipRequest.mentor_id == current_user.id)
        .order_by(MentorshipRequest.requested_at.desc())
    ).all()
    return render_template(
        "mentorship/requests.html",
        requests=requests,
        active=[],
        mentor_view=True,
        response_form=ResponseForm(),
    )


@bp.post("/requests/<int:request_id>/respond")
@roles_required("mentor")
def respond(request_id):
    mentorship_request = db.get_or_404(MentorshipRequest, request_id)
    if mentorship_request.mentor_id != current_user.id:
        abort(403)
    if mentorship_request.status != "pending":
        abort(409)
    form = ResponseForm()
    if not form.validate_on_submit():
        abort(400)
    if form.decision.data == "accepted":
        active = db.session.scalar(
            db.select(Mentorship).filter_by(
                freelancer_id=mentorship_request.freelancer_id,
                mentor_id=current_user.id,
                status="active",
            )
        )
        if active:
            abort(409)
        db.session.add(
            Mentorship(
                freelancer_id=mentorship_request.freelancer_id,
                mentor_id=current_user.id,
            )
        )
    mentorship_request.status = form.decision.data
    notify(
        mentorship_request.freelancer_id,
        f"{current_user.full_name} {form.decision.data} your mentorship request.",
        "mentorship_response",
    )
    db.session.commit()
    flash(f"Mentorship request {form.decision.data}.", "success")
    return redirect(url_for("mentorship.received_requests"))


@bp.get("/mentees")
@roles_required("mentor")
def mentees():
    mentorships = db.session.scalars(
        db.select(Mentorship).where(
            Mentorship.mentor_id == current_user.id, Mentorship.status == "active"
        )
    ).all()
    return render_template("mentorship/mentees.html", mentorships=mentorships)


@bp.get("/<int:mentorship_id>/workspace")
@login_required
def workspace(mentorship_id):
    mentorship = _active_participant(mentorship_id)
    mentor_view = current_user.id == mentorship.mentor_id
    goal_form = GoalForm(prefix="goal")
    progress_form = ProgressUpdateForm(prefix="progress")
    progress_form.goal_id.choices = _goal_choices(mentorship)
    feedback_form = FeedbackForm(prefix="feedback")
    feedback_form.goal_id.choices = _goal_choices(mentorship)
    feedback_form.progress_update_id.choices = _progress_choices(mentorship)

    activities = [
        {
            "date": mentorship.start_date,
            "text": "Mentorship started.",
            "type": "start",
        }
    ]
    for goal in mentorship.goals:
        activities.append(
            {"date": goal.created_at, "text": f"Goal created: {goal.title}", "type": "goal"}
        )
        if goal.completed_at:
            activities.append(
                {
                    "date": goal.completed_at,
                    "text": f"Goal completed: {goal.title}",
                    "type": "completed",
                }
            )
    for update in mentorship.progress_updates:
        activities.append(
            {
                "date": update.created_at,
                "text": f"{mentorship.freelancer.full_name} posted a progress update.",
                "type": "progress",
            }
        )
    for feedback in mentorship.feedback_entries:
        activities.append(
            {
                "date": feedback.created_at,
                "text": f"{mentorship.mentor.full_name} provided feedback.",
                "type": "feedback",
            }
        )
    activities.sort(key=lambda item: item["date"], reverse=True)

    return render_template(
        "mentorship/workspace.html",
        mentorship=mentorship,
        mentor_view=mentor_view,
        goals=sorted(mentorship.goals, key=lambda item: item.created_at, reverse=True),
        updates=sorted(
            mentorship.progress_updates,
            key=lambda item: item.created_at,
            reverse=True,
        ),
        feedback_entries=sorted(
            mentorship.feedback_entries,
            key=lambda item: item.created_at,
            reverse=True,
        ),
        activities=activities,
        goal_form=goal_form,
        progress_form=progress_form,
        feedback_form=feedback_form,
        action_form=WorkspaceActionForm(),
    )


@bp.post("/<int:mentorship_id>/goals")
@login_required
def create_goal(mentorship_id):
    mentorship = _active_participant(mentorship_id)
    form = GoalForm(prefix="goal")
    if not form.validate_on_submit():
        _form_error(form, "Enter a valid mentorship goal.")
        return redirect(url_for("mentorship.workspace", mentorship_id=mentorship.id))
    goal = MentorshipGoal(
        mentorship=mentorship,
        title=form.title.data.strip(),
        description=form.description.data.strip(),
    )
    db.session.add(goal)
    other = _other_participant(mentorship)
    notify(
        other.id,
        f"A new mentorship goal was added: {goal.title}.",
        "mentorship_goal",
    )
    db.session.commit()
    flash("Mentorship goal created.", "success")
    return redirect(url_for("mentorship.workspace", mentorship_id=mentorship.id))


@bp.post("/<int:mentorship_id>/goals/<int:goal_id>/complete")
@login_required
def complete_goal(mentorship_id, goal_id):
    mentorship = _active_participant(mentorship_id)
    if not WorkspaceActionForm().validate_on_submit():
        abort(400)
    goal = db.get_or_404(MentorshipGoal, goal_id)
    if goal.mentorship_id != mentorship.id:
        abort(403)
    if goal.status != "completed":
        goal.status = "completed"
        goal.completed_at = datetime.now(timezone.utc)
        goal.updated_at = goal.completed_at
        other = _other_participant(mentorship)
        notify(
            other.id,
            f"Mentorship goal completed: {goal.title}.",
            "mentorship_goal_completed",
        )
        db.session.commit()
        flash("Goal marked as completed.", "success")
    return redirect(url_for("mentorship.workspace", mentorship_id=mentorship.id))


@bp.post("/<int:mentorship_id>/progress")
@login_required
def create_progress(mentorship_id):
    mentorship = _active_participant(mentorship_id)
    if current_user.id != mentorship.freelancer_id:
        abort(403)
    form = ProgressUpdateForm(prefix="progress")
    form.goal_id.choices = _goal_choices(mentorship)
    if not form.validate_on_submit():
        _form_error(form, "Enter a valid progress update.")
        return redirect(url_for("mentorship.workspace", mentorship_id=mentorship.id))
    goal_id = form.goal_id.data or None
    if goal_id and not any(goal.id == goal_id for goal in mentorship.goals):
        abort(400)
    db.session.add(
        MentorshipProgressUpdate(
            mentorship=mentorship,
            author_id=current_user.id,
            goal_id=goal_id,
            content=form.content.data.strip(),
        )
    )
    notify(
        mentorship.mentor_id,
        f"{current_user.full_name} posted a mentorship progress update.",
        "mentorship_progress",
    )
    db.session.commit()
    flash("Progress update shared with your mentor.", "success")
    return redirect(url_for("mentorship.workspace", mentorship_id=mentorship.id))


@bp.post("/<int:mentorship_id>/feedback")
@login_required
def create_feedback(mentorship_id):
    mentorship = _active_participant(mentorship_id)
    if current_user.id != mentorship.mentor_id:
        abort(403)
    form = FeedbackForm(prefix="feedback")
    form.goal_id.choices = _goal_choices(mentorship)
    form.progress_update_id.choices = _progress_choices(mentorship)
    if not form.validate_on_submit():
        _form_error(form, "Enter valid mentor feedback.")
        return redirect(url_for("mentorship.workspace", mentorship_id=mentorship.id))
    goal_id = form.goal_id.data or None
    update_id = form.progress_update_id.data or None
    if goal_id and not any(goal.id == goal_id for goal in mentorship.goals):
        abort(400)
    if update_id and not any(
        update.id == update_id for update in mentorship.progress_updates
    ):
        abort(400)
    db.session.add(
        MentorshipFeedback(
            mentorship=mentorship,
            mentor_id=current_user.id,
            progress_update_id=update_id,
            goal_id=goal_id,
            content=form.content.data.strip(),
        )
    )
    notify(
        mentorship.freelancer_id,
        f"{current_user.full_name} provided feedback on your mentorship progress.",
        "mentorship_feedback",
    )
    db.session.commit()
    flash("Feedback shared with your mentee.", "success")
    return redirect(url_for("mentorship.workspace", mentorship_id=mentorship.id))
