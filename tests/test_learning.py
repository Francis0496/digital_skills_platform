import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Course, CourseCategory, Enrollment, Lesson, LessonProgress
from app.courses.routes import _lesson_video_source


def login(client, email="learner@example.com"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": "SecurePass123!"},
        follow_redirects=True,
    )


@pytest.fixture()
def course_factory(app):
    def create_course(published=True, lesson_count=2):
        category = CourseCategory(name="Web Development", description="Web skills")
        course = Course(
            category=category,
            title="Web Fundamentals",
            description="Learn practical web development foundations.",
            difficulty_level="Beginner",
            is_published=published,
        )
        for index in range(1, lesson_count + 1):
            course.lessons.append(
                Lesson(
                    title=f"Lesson {index}",
                    content=f"Content for lesson {index}",
                    lesson_order=index,
                )
            )
        db.session.add(course)
        db.session.commit()
        return course

    return create_course


def test_course_01_only_published_courses_are_public(client, course_factory):
    published = course_factory()
    draft = Course(
        category=published.category,
        title="Draft Course",
        description="Not public",
        is_published=False,
    )
    db.session.add(draft)
    db.session.commit()

    response = client.get("/courses/")
    assert b"Web Fundamentals" in response.data
    assert b"Draft Course" not in response.data
    assert client.get(f"/courses/{draft.id}").status_code == 404


def test_course_02_admin_can_view_draft(client, course_factory, user_factory):
    course = course_factory(published=False)
    user_factory(role_name="administrator")
    login(client)
    response = client.get(f"/courses/{course.id}")
    assert response.status_code == 200
    assert b"Draft" in response.data


@pytest.mark.parametrize("role_name", ("freelancer", "mentor", "client"))
def test_course_03_non_admin_cannot_manage_learning(client, user_factory, role_name):
    user_factory(role_name=role_name)
    login(client)
    assert client.get("/admin/learning").status_code == 403
    assert client.get("/admin/categories/new").status_code == 403
    assert client.get("/admin/courses/new").status_code == 403


def test_course_04_admin_creates_category_course_and_lesson(client, user_factory):
    user_factory(role_name="administrator")
    login(client)
    client.post(
        "/admin/categories/new",
        data={"name": "Digital Marketing", "description": "Marketing skills"},
    )
    category = db.session.scalar(
        db.select(CourseCategory).filter_by(name="Digital Marketing")
    )
    response = client.post(
        "/admin/courses/new",
        data={
            "category_id": category.id,
            "title": "Marketing Basics",
            "description": "Learn campaign fundamentals",
            "difficulty_level": "Beginner",
            "is_published": "y",
        },
        follow_redirects=True,
    )
    course = db.session.scalar(db.select(Course).filter_by(title="Marketing Basics"))
    assert b"Course created" in response.data
    assert course.is_published is True

    response = client.post(
        f"/admin/courses/{course.id}/lessons/new",
        data={"title": "Introduction", "content": "Lesson content", "lesson_order": 1},
        follow_redirects=True,
    )
    assert b"Lesson created" in response.data
    assert len(course.lessons) == 1


def test_course_05_duplicate_category_name_is_rejected(client, user_factory):
    user_factory(role_name="administrator")
    db.session.add(CourseCategory(name="Design"))
    db.session.commit()
    login(client)
    response = client.post("/admin/categories/new", data={"name": "Design"})
    assert b"already exists" in response.data


def test_course_05b_admin_category_collection_has_clear_management_ui(
    client, user_factory, course_factory
):
    course_factory()
    user_factory(role_name="administrator")
    login(client)

    response = client.get("/admin/learning")

    assert response.status_code == 200
    assert b"learning-category-grid" in response.data
    assert b"Course library" in response.data
    assert b"<strong>1</strong><span>category</span>" in response.data
    assert b"2 lessons" in response.data
    assert b"Edit category" in response.data


def test_course_06_database_enforces_lesson_order_uniqueness(app, course_factory):
    course = course_factory(lesson_count=1)
    db.session.add(
        Lesson(course=course, title="Duplicate", content="Content", lesson_order=1)
    )
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_enrol_01_freelancer_can_enrol_once(client, user_factory, course_factory):
    user = user_factory()
    course = course_factory()
    login(client)
    response = client.post(f"/courses/{course.id}/enrol", follow_redirects=True)
    assert b"You are enrolled" in response.data
    assert db.session.scalar(
        db.select(Enrollment).filter_by(user_id=user.id, course_id=course.id)
    ) is not None

    response = client.post(f"/courses/{course.id}/enrol", follow_redirects=True)
    assert b"already enrolled" in response.data
    assert db.session.scalar(db.select(db.func.count(Enrollment.id))) == 1


@pytest.mark.parametrize("role_name", ("mentor", "client", "administrator"))
def test_enrol_02_non_freelancers_cannot_enrol(client, user_factory, course_factory, role_name):
    user_factory(role_name=role_name)
    course = course_factory()
    login(client)
    assert client.post(f"/courses/{course.id}/enrol").status_code == 403


def test_enrol_03_draft_course_cannot_be_enrolled(client, user_factory, course_factory):
    user_factory()
    course = course_factory(published=False)
    login(client)
    assert client.post(f"/courses/{course.id}/enrol").status_code == 404


def test_learning_01_unenrolled_learner_cannot_open_lesson(client, user_factory, course_factory):
    user_factory()
    course = course_factory()
    login(client)
    assert client.get(f"/courses/learn/999/{course.lessons[0].id}").status_code == 404


def test_learning_01b_lesson_content_uses_an_isolated_scroll_region(
    client, user_factory, course_factory
):
    user = user_factory()
    course = course_factory()
    enrollment = Enrollment(user=user, course=course)
    db.session.add(enrollment)
    db.session.commit()
    login(client)

    response = client.get(f"/courses/learn/{enrollment.id}/{course.lessons[0].id}")

    assert response.status_code == 200
    assert b'class="lesson-content-scroll"' in response.data
    assert b'role="region"' in response.data
    assert b'tabindex="0"' in response.data
    assert b'class="lesson-reader-actions"' in response.data


@pytest.mark.parametrize(
    ("video_url", "kind", "expected"),
    (
        (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "embed",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0",
        ),
        (
            "https://vimeo.com/76979871",
            "embed",
            "https://player.vimeo.com/video/76979871",
        ),
        ("https://cdn.example.com/lesson.mp4", "file", "lesson.mp4"),
    ),
)
def test_learning_01c_approved_video_sources_are_normalized(
    video_url, kind, expected
):
    source = _lesson_video_source(video_url)
    assert source["kind"] == kind
    assert expected in source["url"]


def test_learning_01d_lesson_video_plays_inside_platform(
    client, user_factory, course_factory
):
    user = user_factory()
    course = course_factory()
    course.lessons[0].video_url = "https://youtu.be/dQw4w9WgXcQ"
    enrollment = Enrollment(user=user, course=course)
    db.session.add(enrollment)
    db.session.commit()
    login(client)

    response = client.get(f"/courses/learn/{enrollment.id}/{course.lessons[0].id}")

    assert response.status_code == 200
    assert b'class="lesson-video-frame"' in response.data
    assert b"youtube-nocookie.com/embed/dQw4w9WgXcQ" in response.data
    assert b"allowfullscreen" in response.data
    assert b">Open lesson video</a>" not in response.data


def test_learning_01e_unapproved_video_provider_is_not_embedded():
    assert _lesson_video_source("https://untrusted.example/video/123") is None


def test_learning_02_learner_cannot_open_another_enrollment(client, user_factory, course_factory):
    user_factory()
    other = user_factory(email="other@example.com")
    course = course_factory()
    enrollment = Enrollment(user=other, course=course)
    db.session.add(enrollment)
    db.session.commit()
    login(client)
    assert client.get(
        f"/courses/learn/{enrollment.id}/{course.lessons[0].id}"
    ).status_code == 403


def test_learning_03_completion_calculates_progress(client, user_factory, course_factory):
    user = user_factory()
    course = course_factory(lesson_count=2)
    enrollment = Enrollment(user=user, course=course)
    db.session.add(enrollment)
    db.session.commit()
    login(client)

    first, second = course.lessons
    client.post(f"/courses/learn/{enrollment.id}/{first.id}/complete")
    db.session.refresh(enrollment)
    assert enrollment.progress_percentage == 50
    assert enrollment.completion_status == "in_progress"

    client.post(f"/courses/learn/{enrollment.id}/{second.id}/complete")
    db.session.refresh(enrollment)
    assert enrollment.progress_percentage == 100
    assert enrollment.completion_status == "completed"


def test_learning_04_lesson_from_other_course_is_forbidden(client, user_factory, course_factory):
    user = user_factory()
    first_course = course_factory()
    second_category = CourseCategory(name="Design")
    second_course = Course(
        category=second_category,
        title="Design Basics",
        description="Design course",
        is_published=True,
    )
    other_lesson = Lesson(
        course=second_course, title="Other Lesson", content="Other", lesson_order=1
    )
    enrollment = Enrollment(user=user, course=first_course)
    db.session.add_all([second_course, enrollment])
    db.session.commit()
    login(client)
    assert client.post(
        f"/courses/learn/{enrollment.id}/{other_lesson.id}/complete"
    ).status_code == 403


def test_learning_05_progress_constraint_prevents_duplicates(app, user_factory, course_factory):
    user = user_factory()
    course = course_factory(lesson_count=1)
    enrollment = Enrollment(user=user, course=course)
    db.session.add(enrollment)
    db.session.flush()
    db.session.add_all(
        [
            LessonProgress(enrollment=enrollment, lesson=course.lessons[0], completed=True),
            LessonProgress(enrollment=enrollment, lesson=course.lessons[0], completed=True),
        ]
    )
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
