from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.auth.decorators import roles_required
from app.extensions import db
from app.models import Course, CourseCategory, Enrollment, FreelanceOpportunity, JobApplication, Lesson, MentorProfile, Mentorship, MentorshipRequest, Notification, Role, Skill, User
from . import bp
from .forms import ActionForm, CategoryForm, CourseForm, LessonForm, SkillAdminForm

@bp.get("/")
@roles_required("administrator")
def dashboard():
    counts={"users":db.session.scalar(db.select(db.func.count(User.id))),"freelancers":_role_count("freelancer"),"mentors":_role_count("mentor"),"clients":_role_count("client"),"courses":db.session.scalar(db.select(db.func.count(Course.id))),"opportunities":db.session.scalar(db.select(db.func.count(FreelanceOpportunity.id)).where(FreelanceOpportunity.status=="active")),"applications":db.session.scalar(db.select(db.func.count(JobApplication.id))),"mentorships":db.session.scalar(db.select(db.func.count(Mentorship.id)).where(Mentorship.status=="active"))}
    recent_users=db.session.scalars(db.select(User).order_by(User.created_at.desc()).limit(5)).all()
    return render_template("admin/dashboard.html",counts=counts,recent_users=recent_users)

@bp.get("/users")
@roles_required("administrator")
def users():
    query=request.args.get("q","").strip(); statement=db.select(User).order_by(User.created_at.desc())
    if query: statement=statement.where(db.or_(User.full_name.ilike(f"%{query}%"),User.email.ilike(f"%{query}%")))
    return render_template("admin/users.html",users=db.session.scalars(statement).all(),query=query,action_form=ActionForm())

@bp.post("/users/<int:user_id>/toggle-active")
@roles_required("administrator")
def toggle_user(user_id):
    if not ActionForm().validate_on_submit(): abort(400)
    user=db.get_or_404(User,user_id)
    if user.id==current_user.id: abort(400)
    user.is_active=not user.is_active; db.session.commit(); flash(f"User {'activated' if user.is_active else 'deactivated'}.","success"); return redirect(url_for("admin.users"))

@bp.get("/skills")
@roles_required("administrator")
def skills():
    return render_template("admin/skills.html",skills=db.session.scalars(db.select(Skill).order_by(Skill.name)).all())

@bp.route("/skills/new",methods=["GET","POST"])
@roles_required("administrator")
def create_skill(): return _skill_form(Skill())

@bp.route("/skills/<int:skill_id>/edit",methods=["GET","POST"])
@roles_required("administrator")
def edit_skill(skill_id): return _skill_form(db.get_or_404(Skill,skill_id))

@bp.get("/mentorships")
@roles_required("administrator")
def mentorships():
    requests=db.session.scalars(db.select(MentorshipRequest).order_by(MentorshipRequest.requested_at.desc())).all(); active=db.session.scalars(db.select(Mentorship).order_by(Mentorship.start_date.desc())).all()
    return render_template("admin/mentorships.html",requests=requests,mentorships=active)


@bp.get("/learning")
@roles_required("administrator")
def learning():
    categories = db.session.scalars(
        db.select(CourseCategory).order_by(CourseCategory.name)
    ).all()
    courses = db.session.scalars(db.select(Course).order_by(Course.created_at.desc())).all()
    return render_template("admin/learning.html", categories=categories, courses=courses)


@bp.route("/categories/new", methods=["GET", "POST"])
@roles_required("administrator")
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        duplicate = db.session.scalar(db.select(CourseCategory).filter_by(name=name))
        if duplicate:
            form.name.errors.append("A category with this name already exists.")
        else:
            db.session.add(
                CourseCategory(name=name, description=_clean_optional(form.description.data))
            )
            db.session.commit()
            flash("Category created.", "success")
            return redirect(url_for("admin.learning"))
    return render_template("admin/category_form.html", form=form, page_title="New category")


@bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@roles_required("administrator")
def edit_category(category_id):
    category = db.get_or_404(CourseCategory, category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        name = form.name.data.strip()
        duplicate = db.session.scalar(
            db.select(CourseCategory).where(
                CourseCategory.name == name, CourseCategory.id != category.id
            )
        )
        if duplicate:
            form.name.errors.append("A category with this name already exists.")
        else:
            category.name = name
            category.description = _clean_optional(form.description.data)
            db.session.commit()
            flash("Category updated.", "success")
            return redirect(url_for("admin.learning"))
    return render_template("admin/category_form.html", form=form, page_title="Edit category")


@bp.route("/courses/new", methods=["GET", "POST"])
@roles_required("administrator")
def create_course():
    form = CourseForm()
    _set_category_choices(form)
    if form.validate_on_submit():
        course = Course()
        _apply_course_form(course, form)
        db.session.add(course)
        db.session.commit()
        flash("Course created.", "success")
        return redirect(url_for("admin.edit_course", course_id=course.id))
    return render_template("admin/course_form.html", form=form, course=None)


@bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@roles_required("administrator")
def edit_course(course_id):
    course = db.get_or_404(Course, course_id)
    form = CourseForm(obj=course)
    _set_category_choices(form)
    if form.validate_on_submit():
        _apply_course_form(course, form)
        db.session.commit()
        flash("Course updated.", "success")
        return redirect(url_for("admin.edit_course", course_id=course.id))
    return render_template("admin/course_form.html", form=form, course=course)


@bp.route("/courses/<int:course_id>/lessons/new", methods=["GET", "POST"])
@roles_required("administrator")
def create_lesson(course_id):
    course = db.get_or_404(Course, course_id)
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(course=course)
        _apply_lesson_form(lesson, form)
        db.session.add(lesson)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.lesson_order.errors.append("This lesson order is already used in the course.")
        else:
            flash("Lesson created.", "success")
            return redirect(url_for("admin.edit_course", course_id=course.id))
    return render_template("admin/lesson_form.html", form=form, course=course, lesson=None)


@bp.route("/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@roles_required("administrator")
def edit_lesson(lesson_id):
    lesson = db.get_or_404(Lesson, lesson_id)
    form = LessonForm(obj=lesson)
    if form.validate_on_submit():
        _apply_lesson_form(lesson, form)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.lesson_order.errors.append("This lesson order is already used in the course.")
        else:
            flash("Lesson updated.", "success")
            return redirect(url_for("admin.edit_course", course_id=lesson.course_id))
    return render_template("admin/lesson_form.html", form=form, course=lesson.course, lesson=lesson)


def _set_category_choices(form):
    categories = db.session.scalars(
        db.select(CourseCategory).order_by(CourseCategory.name)
    ).all()
    form.category_id.choices = [(category.id, category.name) for category in categories]


def _apply_course_form(course, form):
    course.category_id = form.category_id.data
    course.title = form.title.data.strip()
    course.description = form.description.data.strip()
    course.difficulty_level = _clean_optional(form.difficulty_level.data)
    course.image = _clean_optional(form.image.data)
    course.is_published = form.is_published.data


def _apply_lesson_form(lesson, form):
    lesson.title = form.title.data.strip()
    lesson.content = form.content.data.strip()
    lesson.video_url = _clean_optional(form.video_url.data)
    lesson.lesson_order = form.lesson_order.data


def _clean_optional(value):
    value = value.strip() if value else ""
    return value or None

def _role_count(role_name):
    return db.session.scalar(db.select(db.func.count(User.id)).join(User.role).where(Role.name==role_name))

def _skill_form(skill):
    form=SkillAdminForm(obj=skill)
    if form.validate_on_submit():
        name=form.name.data.strip(); duplicate=db.session.scalar(db.select(Skill).where(Skill.name==name,Skill.id!=skill.id)) if skill.id else db.session.scalar(db.select(Skill).filter_by(name=name))
        if duplicate: form.name.errors.append("A skill with this name already exists.")
        else:
            skill.name=name; skill.description=_clean_optional(form.description.data); db.session.add(skill); db.session.commit(); flash("Skill saved.","success"); return redirect(url_for("admin.skills"))
    return render_template("admin/skill_form.html",form=form,skill=skill if skill.id else None)
