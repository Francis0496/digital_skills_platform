from datetime import datetime, timezone
from pathlib import PurePosixPath
import re
from urllib.parse import parse_qs, urlparse

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.auth.decorators import roles_required
from app.extensions import db
from app.models import Course, CourseCategory, Enrollment, Lesson, LessonProgress
from app.admin.forms import ActionForm
from . import bp
from app.notifications.service import notify


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{6,20}$")


def _lesson_video_source(video_url):
    """Return a safe player source for approved providers or direct video files."""
    if not video_url:
        return None
    parsed = urlparse(video_url.strip())
    if parsed.scheme not in {"http", "https"}:
        return None
    host = (parsed.hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host

    video_id = None
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith(("/embed/", "/shorts/")):
            video_id = parsed.path.strip("/").split("/")[1]
    if video_id and VIDEO_ID_PATTERN.fullmatch(video_id):
        return {
            "kind": "embed",
            "url": f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0",
            "provider": "YouTube",
        }

    if host in {"vimeo.com", "player.vimeo.com"}:
        parts = [part for part in parsed.path.split("/") if part]
        video_id = next((part for part in reversed(parts) if part.isdigit()), None)
        if video_id:
            return {
                "kind": "embed",
                "url": f"https://player.vimeo.com/video/{video_id}",
                "provider": "Vimeo",
            }

    extension = PurePosixPath(parsed.path).suffix.lower()
    if extension in {".mp4", ".webm", ".ogg"}:
        return {"kind": "file", "url": video_url.strip(), "provider": "Video"}
    return None


@bp.get("/")
def catalogue():
    statement = db.select(Course).where(Course.is_published.is_(True))
    category_id = request.args.get("category", type=int)
    difficulty = request.args.get("difficulty", "").strip()
    if category_id:
        statement = statement.where(Course.category_id == category_id)
    if difficulty:
        statement = statement.where(Course.difficulty_level == difficulty)
    courses = db.session.scalars(statement.order_by(Course.created_at.desc())).all()
    categories = db.session.scalars(
        db.select(CourseCategory).order_by(CourseCategory.name)
    ).all()
    return render_template(
        "courses/catalogue.html",
        courses=courses,
        categories=categories,
        selected_category=category_id,
        selected_difficulty=difficulty,
    )


@bp.get("/<int:course_id>")
def detail(course_id):
    course = db.get_or_404(Course, course_id)
    is_admin = current_user.is_authenticated and current_user.role_name == "administrator"
    if not course.is_published and not is_admin:
        abort(404)
    enrollment = None
    if current_user.is_authenticated and current_user.role_name == "freelancer":
        enrollment = db.session.scalar(
            db.select(Enrollment).filter_by(
                user_id=current_user.id, course_id=course.id
            )
        )
    return render_template(
        "courses/detail.html", course=course, enrollment=enrollment, action_form=ActionForm()
    )


@bp.post("/<int:course_id>/enrol")
@roles_required("freelancer")
def enrol(course_id):
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)
    course = db.get_or_404(Course, course_id)
    if not course.is_published:
        abort(404)
    existing = db.session.scalar(
        db.select(Enrollment).filter_by(user_id=current_user.id, course_id=course.id)
    )
    if existing:
        flash("You are already enrolled in this course.", "error")
        return redirect(url_for("courses.detail", course_id=course.id))
    enrollment = Enrollment(user=current_user, course=course)
    db.session.add(enrollment)
    notify(current_user.id, f"You enrolled in {course.title}.", "course_enrollment")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("You are already enrolled in this course.", "error")
    else:
        flash("You are enrolled. Start learning when you are ready.", "success")
    return redirect(url_for("courses.detail", course_id=course.id))


@bp.get("/mine")
@roles_required("freelancer")
def my_courses():
    enrollments = db.session.scalars(
        db.select(Enrollment)
        .where(Enrollment.user_id == current_user.id)
        .order_by(Enrollment.enrolled_at.desc())
    ).all()
    return render_template("courses/my_courses.html", enrollments=enrollments)


@bp.get("/learn/<int:enrollment_id>/<int:lesson_id>")
@roles_required("freelancer")
def learn(enrollment_id, lesson_id):
    enrollment = db.get_or_404(Enrollment, enrollment_id)
    if enrollment.user_id != current_user.id:
        abort(403)
    lesson = db.get_or_404(Lesson, lesson_id)
    if lesson.course_id != enrollment.course_id:
        abort(403)
    lessons = enrollment.course.lessons
    index = lessons.index(lesson)
    progress = db.session.scalar(
        db.select(LessonProgress).filter_by(
            enrollment_id=enrollment.id, lesson_id=lesson.id
        )
    )
    return render_template(
        "courses/learn.html",
        enrollment=enrollment,
        lesson=lesson,
        lessons=lessons,
        progress=progress,
        previous_lesson=lessons[index - 1] if index > 0 else None,
        next_lesson=lessons[index + 1] if index + 1 < len(lessons) else None,
        action_form=ActionForm(),
        video_source=_lesson_video_source(lesson.video_url),
    )


@bp.post("/learn/<int:enrollment_id>/<int:lesson_id>/complete")
@roles_required("freelancer")
def complete_lesson(enrollment_id, lesson_id):
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)
    enrollment = db.get_or_404(Enrollment, enrollment_id)
    lesson = db.get_or_404(Lesson, lesson_id)
    if enrollment.user_id != current_user.id or lesson.course_id != enrollment.course_id:
        abort(403)

    progress = db.session.scalar(
        db.select(LessonProgress).filter_by(
            enrollment_id=enrollment.id, lesson_id=lesson.id
        )
    )
    if progress is None:
        progress = LessonProgress(enrollment=enrollment, lesson=lesson)
        db.session.add(progress)
    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)
    db.session.flush()

    completed_count = db.session.scalar(
        db.select(db.func.count(LessonProgress.id)).where(
            LessonProgress.enrollment_id == enrollment.id,
            LessonProgress.completed.is_(True),
        )
    )
    if enrollment.course.lessons and completed_count == len(enrollment.course.lessons):
        enrollment.completion_status = "completed"
    db.session.commit()
    flash("Lesson marked complete.", "success")
    return redirect(
        url_for("courses.learn", enrollment_id=enrollment.id, lesson_id=lesson.id)
    )
