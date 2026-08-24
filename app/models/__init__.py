from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


APPROVED_ROLES = ("freelancer", "mentor", "client", "administrator")
PUBLIC_ROLES = ("freelancer", "mentor", "client")


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)

    users = db.relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    phone = db.Column(db.String(30))
    location = db.Column(db.String(120))
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    role = db.relationship("Role", back_populates="users")
    skills = db.relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    mentor_profile = db.relationship(
        "MentorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    enrollments = db.relationship(
        "Enrollment", back_populates="user", cascade="all, delete-orphan"
    )
    portfolio = db.relationship("Portfolio", back_populates="user", uselist=False, cascade="all, delete-orphan")
    opportunities = db.relationship("FreelanceOpportunity", back_populates="client")
    job_applications = db.relationship("JobApplication", back_populates="freelancer")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_name(self):
        return self.role.name if self.role else None

    def __repr__(self):
        return f"<User {self.email}>"


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    users = db.relationship("UserSkill", back_populates="skill")

    def __repr__(self):
        return f"<Skill {self.name}>"


class UserSkill(db.Model):
    __table_args__ = (
        db.UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skill.id"), nullable=False)
    proficiency_level = db.Column(db.String(20))

    user = db.relationship("User", back_populates="skills")
    skill = db.relationship("Skill", back_populates="users")


class MentorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False
    )
    professional_title = db.Column(db.String(120))
    expertise = db.Column(db.Text)
    experience = db.Column(db.Text)
    availability = db.Column(db.Text)

    user = db.relationship("User", back_populates="mentor_profile")


class CourseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    courses = db.relationship("Course", back_populates="category")


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("course_category.id"), nullable=False
    )
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(30))
    image = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    category = db.relationship("CourseCategory", back_populates="courses")
    lessons = db.relationship(
        "Lesson",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Lesson.lesson_order",
    )
    enrollments = db.relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )


class Lesson(db.Model):
    __table_args__ = (
        db.UniqueConstraint("course_id", "lesson_order", name="uq_course_lesson_order"),
    )

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(500))
    lesson_order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    course = db.relationship("Course", back_populates="lessons")
    progress_records = db.relationship(
        "LessonProgress", back_populates="lesson", cascade="all, delete-orphan"
    )


class Enrollment(db.Model):
    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    enrolled_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    completion_status = db.Column(
        db.String(30), nullable=False, default="in_progress"
    )

    user = db.relationship("User", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")
    lesson_progress = db.relationship(
        "LessonProgress", back_populates="enrollment", cascade="all, delete-orphan"
    )

    @property
    def progress_percentage(self):
        lesson_count = len(self.course.lessons)
        if lesson_count == 0:
            return 0
        completed = sum(record.completed for record in self.lesson_progress)
        return round((completed / lesson_count) * 100)


class LessonProgress(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            "enrollment_id", "lesson_id", name="uq_enrollment_lesson_progress"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(
        db.Integer, db.ForeignKey("enrollment.id"), nullable=False
    )
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    completed_at = db.Column(db.DateTime)

    enrollment = db.relationship("Enrollment", back_populates="lesson_progress")
    lesson = db.relationship("Lesson", back_populates="progress_records")


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    title = db.Column(db.String(180))
    description = db.Column(db.Text)
    user = db.relationship("User", back_populates="portfolio")
    projects = db.relationship("PortfolioProject", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolio.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_image = db.Column(db.String(255))
    project_url = db.Column(db.String(500))
    completion_date = db.Column(db.Date)
    portfolio = db.relationship("Portfolio", back_populates="projects")


class FreelanceOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    budget = db.Column(db.Numeric(12, 2))
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    client = db.relationship("User", back_populates="opportunities")
    applications = db.relationship("JobApplication", back_populates="opportunity", cascade="all, delete-orphan")

    @property
    def effective_status(self):
        from datetime import date
        status = self.status or "active"
        if status == "active" and self.deadline and self.deadline < date.today():
            return "expired"
        return status

    @property
    def accepts_applications(self):
        return self.effective_status == "active"


class JobApplication(db.Model):
    __table_args__ = (db.UniqueConstraint("opportunity_id", "freelancer_id", name="uq_opportunity_freelancer_application"),)
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("freelance_opportunity.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    cover_message = db.Column(db.Text, nullable=False)
    proposed_amount = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(30), nullable=False, default="pending")
    submitted_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    opportunity = db.relationship("FreelanceOpportunity", back_populates="applications")
    freelancer = db.relationship("User", back_populates="job_applications")


class MentorshipRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="pending")
    requested_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    freelancer = db.relationship("User", foreign_keys=[freelancer_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])


class Mentorship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), nullable=False, default="active")
    freelancer = db.relationship("User", foreign_keys=[freelancer_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", back_populates="notifications")


def seed_roles():
    created = 0
    for role_name in APPROVED_ROLES:
        if db.session.scalar(db.select(Role).filter_by(name=role_name)) is None:
            db.session.add(Role(name=role_name))
            created += 1
    db.session.commit()
    return created
