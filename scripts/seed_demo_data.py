"""Populate the platform with additional realistic demo data.

Idempotent: safe to run more than once. Existing rows (matched by unique
fields such as email, skill name, or course title) are left untouched and
only missing records are created.

Usage:
    python scripts/seed_demo_data.py
"""
import os
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import (
    Course,
    CourseCategory,
    Enrollment,
    FreelanceOpportunity,
    JobApplication,
    Lesson,
    LessonProgress,
    MentorProfile,
    Mentorship,
    MentorshipFeedback,
    MentorshipGoal,
    MentorshipProgressUpdate,
    MentorshipRequest,
    Notification,
    Portfolio,
    PortfolioProject,
    Role,
    Skill,
    User,
    UserSkill,
    seed_roles,
)

DEMO_PASSWORD = "DemoPass123!"


def now():
    return datetime.now(timezone.utc)


def get_or_create_user(full_name, email, role_name, **extra):
    user = db.session.scalar(db.select(User).filter_by(email=email))
    if user is not None:
        return user, False
    role = db.session.scalar(db.select(Role).filter_by(name=role_name))
    user = User(full_name=full_name, email=email, role=role, **extra)
    user.set_password(DEMO_PASSWORD)
    db.session.add(user)
    db.session.flush()
    return user, True


def get_or_create_skill(name, description):
    skill = db.session.scalar(db.select(Skill).filter_by(name=name))
    if skill is not None:
        return skill
    skill = Skill(name=name, description=description)
    db.session.add(skill)
    db.session.flush()
    return skill


def ensure_user_skill(user, skill, proficiency_level):
    existing = db.session.scalar(
        db.select(UserSkill).filter_by(user_id=user.id, skill_id=skill.id)
    )
    if existing is not None:
        return existing
    link = UserSkill(user=user, skill=skill, proficiency_level=proficiency_level)
    db.session.add(link)
    return link


def get_or_create_course(category, title, description, difficulty_level, image, lessons):
    course = db.session.scalar(db.select(Course).filter_by(title=title))
    created = False
    if course is None:
        course = Course(
            category=category,
            title=title,
            description=description,
            difficulty_level=difficulty_level,
            image=image,
            is_published=True,
        )
        db.session.add(course)
        db.session.flush()
        created = True
    if created:
        for order, (lesson_title, content, video_url) in enumerate(lessons, start=1):
            db.session.add(
                Lesson(
                    course=course,
                    title=lesson_title,
                    content=content,
                    video_url=video_url,
                    lesson_order=order,
                )
            )
        db.session.flush()
    return course


def ensure_enrollment(user, course, completion_status="in_progress", completed_lesson_titles=None):
    enrollment = db.session.scalar(
        db.select(Enrollment).filter_by(user_id=user.id, course_id=course.id)
    )
    if enrollment is None:
        enrollment = Enrollment(user=user, course=course, completion_status=completion_status)
        db.session.add(enrollment)
        db.session.flush()
        db.session.add(
            Notification(
                user=user,
                message=f"You enrolled in {course.title}.",
                notification_type="course_enrollment",
            )
        )
    if completed_lesson_titles:
        for lesson in course.lessons:
            if lesson.title in completed_lesson_titles:
                progress = db.session.scalar(
                    db.select(LessonProgress).filter_by(
                        enrollment_id=enrollment.id, lesson_id=lesson.id
                    )
                )
                if progress is None:
                    db.session.add(
                        LessonProgress(
                            enrollment=enrollment,
                            lesson=lesson,
                            completed=True,
                            completed_at=now(),
                        )
                    )
    return enrollment


def ensure_portfolio(user, title, description, projects):
    portfolio = db.session.scalar(db.select(Portfolio).filter_by(user_id=user.id))
    if portfolio is None:
        portfolio = Portfolio(user=user, title=title, description=description)
        db.session.add(portfolio)
        db.session.flush()
    for project_title, project_description, completion_date, url in projects:
        existing = db.session.scalar(
            db.select(PortfolioProject).filter_by(
                portfolio_id=portfolio.id, title=project_title
            )
        )
        if existing is None:
            db.session.add(
                PortfolioProject(
                    portfolio=portfolio,
                    title=project_title,
                    description=project_description,
                    completion_date=completion_date,
                    project_url=url,
                )
            )
    return portfolio


def get_or_create_opportunity(client, title, description, category, budget, deadline, status="active"):
    opportunity = db.session.scalar(db.select(FreelanceOpportunity).filter_by(title=title))
    if opportunity is not None:
        return opportunity, False
    opportunity = FreelanceOpportunity(
        client=client,
        title=title,
        description=description,
        category=category,
        budget=budget,
        deadline=deadline,
        status=status,
    )
    db.session.add(opportunity)
    db.session.flush()
    return opportunity, True


def ensure_application(opportunity, freelancer, cover_message, proposed_amount, status):
    existing = db.session.scalar(
        db.select(JobApplication).filter_by(
            opportunity_id=opportunity.id, freelancer_id=freelancer.id
        )
    )
    if existing is not None:
        return existing
    application = JobApplication(
        opportunity=opportunity,
        freelancer=freelancer,
        cover_message=cover_message,
        proposed_amount=proposed_amount,
        status=status,
    )
    db.session.add(application)
    db.session.flush()
    db.session.add(
        Notification(
            user=opportunity.client,
            message=f"New application received for {opportunity.title}.",
            notification_type="application_received",
        )
    )
    if status != "pending":
        db.session.add(
            Notification(
                user=freelancer,
                message=f"Your application for {opportunity.title} is now {status.replace('_', ' ')}.",
                notification_type="application_status",
            )
        )
    return application


def ensure_mentor_profile(user, professional_title, expertise, experience, availability):
    profile = db.session.scalar(db.select(MentorProfile).filter_by(user_id=user.id))
    if profile is not None:
        return profile
    profile = MentorProfile(
        user=user,
        professional_title=professional_title,
        expertise=expertise,
        experience=experience,
        availability=availability,
    )
    db.session.add(profile)
    return profile


def ensure_mentorship(freelancer, mentor, message, decision, with_goals=False):
    request = db.session.scalar(
        db.select(MentorshipRequest).filter_by(
            freelancer_id=freelancer.id, mentor_id=mentor.id
        )
    )
    if request is None:
        request = MentorshipRequest(
            freelancer=freelancer, mentor=mentor, message=message, status=decision
        )
        db.session.add(request)
        db.session.flush()
        db.session.add(
            Notification(
                user=mentor,
                message=f"New mentorship request from {freelancer.full_name}.",
                notification_type="mentorship_request",
            )
        )
        if decision != "pending":
            db.session.add(
                Notification(
                    user=freelancer,
                    message=f"{mentor.full_name} {decision} your mentorship request.",
                    notification_type="mentorship_response",
                )
            )

    mentorship = None
    if decision == "accepted":
        mentorship = db.session.scalar(
            db.select(Mentorship).filter_by(freelancer_id=freelancer.id, mentor_id=mentor.id)
        )
        if mentorship is None:
            mentorship = Mentorship(freelancer=freelancer, mentor=mentor, status="active")
            db.session.add(mentorship)
            db.session.flush()
            if with_goals:
                goal = MentorshipGoal(
                    mentorship=mentorship,
                    title="Build a portfolio-ready project",
                    description="Design, build, and deploy a project suitable for showcasing to clients.",
                    status="active",
                )
                db.session.add(goal)
                db.session.flush()
                update = MentorshipProgressUpdate(
                    mentorship=mentorship,
                    author=freelancer,
                    goal=goal,
                    content="Completed the initial project plan and set up the development environment.",
                )
                db.session.add(update)
                db.session.flush()
                db.session.add(
                    MentorshipFeedback(
                        mentorship=mentorship,
                        mentor=mentor,
                        progress_update=update,
                        goal=goal,
                        content="Good start — make sure to add automated tests before moving to the next milestone.",
                    )
                )
    return request, mentorship


def run():
    app = create_app()
    with app.app_context():
        seed_roles()

        # --- Additional skills -------------------------------------------------
        skill_content_writing = get_or_create_skill(
            "Content Writing",
            "Producing articles, website copy, reports, and other written digital content.",
        )
        skill_uiux = get_or_create_skill(
            "UI/UX Design",
            "Designing usable and accessible digital interfaces through wireframing, prototyping, and user research.",
        )
        skill_video_editing = get_or_create_skill(
            "Video Editing",
            "Editing and producing video content using tools such as Adobe Premiere Pro, DaVinci Resolve, or CapCut.",
        )
        skill_social_media = get_or_create_skill(
            "Social Media Management",
            "Planning, scheduling, and managing content and engagement across social media platforms.",
        )
        skill_web_dev = db.session.scalar(db.select(Skill).filter_by(name="Web Development"))
        skill_graphic_design = db.session.scalar(db.select(Skill).filter_by(name="Graphic Design"))
        skill_data_analysis = db.session.scalar(db.select(Skill).filter_by(name="Data Analysis"))
        skill_digital_marketing = db.session.scalar(db.select(Skill).filter_by(name="Digital Marketing"))
        skill_software_dev = db.session.scalar(db.select(Skill).filter_by(name="Software Development"))
        skill_excel = db.session.scalar(db.select(Skill).filter_by(name="Microsoft Excel"))

        # --- Freelancers ---------------------------------------------------------
        aminata, _ = get_or_create_user("Aminata Kamara", "aminata.kamara@example.com", "freelancer")
        mohamed, _ = get_or_create_user("Mohamed Bangura", "mohamed.bangura@example.com", "freelancer")
        fatmata, _ = get_or_create_user("Fatmata Conteh", "fatmata.conteh@example.com", "freelancer")
        abdul, _ = get_or_create_user("Abdul Sesay", "abdul.sesay@example.com", "freelancer")
        isata, _ = get_or_create_user("Isata Turay", "isata.turay@example.com", "freelancer")
        joseph, _ = get_or_create_user("Joseph Koroma", "joseph.koroma@example.com", "freelancer")

        ensure_user_skill(aminata, skill_web_dev, "Intermediate")
        ensure_user_skill(aminata, skill_uiux, "Beginner")
        ensure_user_skill(mohamed, skill_graphic_design, "Advanced")
        ensure_user_skill(mohamed, skill_social_media, "Intermediate")
        ensure_user_skill(fatmata, skill_data_analysis, "Intermediate")
        ensure_user_skill(fatmata, skill_excel, "Advanced")
        ensure_user_skill(abdul, skill_software_dev, "Beginner")
        ensure_user_skill(abdul, skill_web_dev, "Beginner")
        ensure_user_skill(isata, skill_content_writing, "Advanced")
        ensure_user_skill(isata, skill_digital_marketing, "Intermediate")
        ensure_user_skill(joseph, skill_video_editing, "Intermediate")
        ensure_user_skill(joseph, skill_social_media, "Beginner")

        # --- Mentors ---------------------------------------------------------------
        mariama, _ = get_or_create_user("Mariama Jalloh", "mariama.jalloh@example.com", "mentor")
        alhaji, _ = get_or_create_user("Alhaji Bah", "alhaji.bah@example.com", "mentor")
        sallay, _ = get_or_create_user("Sallay Kamara", "sallay.kamara@example.com", "mentor")

        ensure_mentor_profile(
            mariama,
            "UI/UX Designer & Design Mentor",
            "UI/UX Design, Wireframing, Prototyping, Graphic Design, Figma",
            "6 years",
            "Available for mentorship",
        )
        ensure_mentor_profile(
            alhaji,
            "Data Analyst & Analytics Mentor",
            "Data Analysis, Microsoft Excel, Python, Data Visualization",
            "7 years",
            "Available for mentorship",
        )
        ensure_mentor_profile(
            sallay,
            "Digital Marketing Specialist & Career Mentor",
            "Digital Marketing, Social Media Management, Content Strategy, Freelancing",
            "5 years",
            "Available weekday evenings",
        )

        # --- Clients ----------------------------------------------------------------
        precious, _ = get_or_create_user("Precious Johnson", "precious.johnson@example.com", "client")
        samuel, _ = get_or_create_user("Samuel Vandi", "samuel.vandi@example.com", "client")
        rugiatu, _ = get_or_create_user("Rugiatu Sesay", "rugiatu.sesay@example.com", "client")

        # --- Courses & lessons --------------------------------------------------------
        categories = {c.name: c for c in db.session.scalars(db.select(CourseCategory))}

        python_course = get_or_create_course(
            categories["Programming"],
            "Python Programming Basics",
            "An introduction to programming using Python, covering variables, data types, control flow, and functions for learners with no prior coding experience.",
            "Beginner",
            "/static/images/courses/python-programming-basics.webp",
            [
                (
                    "Introduction to Python",
                    "Python is a general-purpose programming language known for its readable syntax and wide use in web development, data analysis, automation, and software engineering.\n\n"
                    "A Python program is made up of statements executed by an interpreter. Unlike some languages, Python does not require you to declare the type of a variable before using it.\n\n"
                    "A simple Python program:\nprint(\"Hello, Digital Skills Platform!\")\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nExplain what Python is and where it is used.\nRun a simple Python script.\nUnderstand what an interpreter does.\n\n"
                    "Practical activity\n\nInstall Python on your computer and write a script that prints your name and one digital skill you want to learn.",
                    "https://www.youtube.com/watch?v=kqtD5dpn9C8",
                ),
                (
                    "Variables and Data Types",
                    "A variable stores a value that can be used and changed throughout a program. Python supports several built-in data types, including integers, floating-point numbers, strings, and booleans.\n\n"
                    "Examples:\nname = \"Aminata\"\nage = 24\nis_freelancer = True\n\n"
                    "Python also provides collection types such as lists and dictionaries for storing multiple values.\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nCreate variables of different data types.\nExplain the difference between a string, an integer, and a boolean.\nUse a list to store multiple related values.\n\n"
                    "Practical activity\n\nWrite a script that stores your name, age, and three skills in variables, then prints them in a formatted sentence.",
                    "https://www.youtube.com/watch?v=cQT33yu9pY8",
                ),
            ],
        )

        data_course = get_or_create_course(
            categories["Data Analytics"],
            "Data Analysis Foundations",
            "Learn the fundamentals of collecting, organising, and interpreting data to support decision-making, using spreadsheet tools and basic statistical concepts.",
            "Beginner",
            "/static/images/courses/data-analysis-foundations.webp",
            [
                (
                    "Introduction to Data Analysis",
                    "Data analysis is the process of inspecting, cleaning, and interpreting data to discover useful information and support decision-making.\n\n"
                    "The typical data analysis workflow includes collecting data, cleaning it to remove errors or inconsistencies, analysing it to identify patterns, and presenting findings clearly.\n\n"
                    "Analysts commonly work with tools such as Microsoft Excel, Python with Pandas, SQL, and visualization software such as Power BI or Tableau.\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nExplain what data analysis involves.\nDescribe the stages of a typical data analysis workflow.\nIdentify common data analysis tools.\n\n"
                    "Practical activity\n\nFind a small dataset (for example, your household's monthly expenses) and identify what questions you could answer by analysing it.",
                    "https://www.youtube.com/watch?v=r-uOLxNrNk8",
                ),
                (
                    "Working with Spreadsheets and Excel Functions",
                    "Spreadsheets organise data into rows and columns and allow calculations to be performed using formulas and functions.\n\n"
                    "Common Excel functions include SUM, AVERAGE, COUNT, and IF for calculations, as well as VLOOKUP and INDEX/MATCH for looking up data across a worksheet.\n\n"
                    "PivotTables allow analysts to summarise large datasets quickly, for example calculating total sales by region or by month.\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nUse basic formulas such as SUM, AVERAGE, and IF.\nExplain the purpose of a lookup function.\nCreate a simple PivotTable summary.\n\n"
                    "Practical activity\n\nCreate a spreadsheet listing ten sample transactions and use SUM and AVERAGE to summarise the total and average amount.",
                    "https://www.youtube.com/watch?v=Vl0H-qTclOg",
                ),
            ],
        )

        design_course = get_or_create_course(
            categories["Graphics Design"],
            "Graphic Design Fundamentals",
            "An introduction to the core principles of visual design, colour, and typography, applied through practical exercises using accessible design tools.",
            "Beginner",
            "/static/images/courses/graphic-design-fundamentals.webp",
            [
                (
                    "Principles of Visual Design",
                    "Good graphic design communicates a message clearly while being visually appealing. This relies on core principles such as balance, contrast, alignment, and hierarchy.\n\n"
                    "Balance refers to the visual weight of elements on a page. Contrast helps important elements stand out, for example using a bold colour for a call-to-action button. Alignment keeps a layout organised and easy to follow. Hierarchy guides the viewer's eye to the most important information first.\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nExplain the principles of balance, contrast, alignment, and hierarchy.\nIdentify these principles in an existing design.\nApply at least one principle to a simple design task.\n\n"
                    "Practical activity\n\nFind a flyer or poster and identify how balance, contrast, alignment, and hierarchy have been used.",
                    "https://www.youtube.com/watch?v=a5KkGqiF3ho",
                ),
                (
                    "Getting Started with Canva",
                    "Canva is a free, browser-based design tool that allows beginners to create professional graphics such as flyers, social media posts, and logos using templates.\n\n"
                    "Key features include drag-and-drop editing, a large library of templates, and tools for adjusting colour, typography, and layout without requiring advanced design software skills.\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nCreate a free Canva account.\nSelect and customise a template.\nExport a finished design for use online or in print.\n\n"
                    "Practical activity\n\nUse Canva to design a simple promotional flyer for a fictional training programme, applying the design principles from the previous lesson.",
                    "https://www.youtube.com/watch?v=8DIizMEP1e8",
                ),
            ],
        )

        uiux_course = get_or_create_course(
            categories["UI/UX Design"],
            "UI/UX Design Foundations",
            "Learn the fundamentals of user-interface and user-experience design, including wireframing, prototyping, and usability principles.",
            "Beginner",
            "/static/images/courses/uiux-design-foundations.webp",
            [
                (
                    "Introduction to UI/UX Design",
                    "User interface (UI) design focuses on the visual layout of a digital product, including buttons, colours, and typography. User experience (UX) design focuses on how the product feels to use, including ease of navigation and how well it solves the user's problem.\n\n"
                    "A well-designed product balances both: it looks good and works well. Common UX methods include user research, wireframing, and usability testing.\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nDistinguish between UI design and UX design.\nExplain why usability matters in digital products.\nIdentify examples of good and poor UX in apps you use daily.\n\n"
                    "Practical activity\n\nChoose an app you use often and list three things about its design that make it easy or difficult to use.",
                    "https://www.youtube.com/watch?v=c9Wg6Cb_YlU",
                ),
                (
                    "Wireframing and Prototyping Basics",
                    "A wireframe is a simple, low-detail sketch of a screen layout used to plan structure and content placement before visual design begins. A prototype is a more interactive version that allows users to click through screens to simulate the finished product.\n\n"
                    "Free tools such as Figma allow designers to create wireframes and prototypes collaboratively and share them with clients for feedback before development starts.\n\n"
                    "Learning objectives\n\nBy the end of this lesson, you should be able to:\n\nExplain the difference between a wireframe and a prototype.\nCreate a basic wireframe for a simple screen.\nExplain why prototyping before development saves time and cost.\n\n"
                    "Practical activity\n\nSketch a wireframe (on paper or in Figma) for the homepage of a freelancing platform, including a navigation bar, a search area, and a list of opportunities.",
                    "https://www.youtube.com/watch?v=c9Wg6Cb_YlU",
                ),
            ],
        )

        web_course = db.session.scalar(db.select(Course).filter_by(title="Web Development Fundamentals"))
        freelancing_course = db.session.scalar(db.select(Course).filter_by(title="Freelancing Fundamentals"))

        # --- Enrollments ------------------------------------------------------------
        ensure_enrollment(aminata, web_course, "in_progress", {"Introduction to Web Development"})
        ensure_enrollment(aminata, uiux_course, "in_progress")
        ensure_enrollment(mohamed, design_course, "completed", {"Principles of Visual Design", "Getting Started with Canva"})
        ensure_enrollment(mohamed, freelancing_course, "in_progress", {"Introduction to Freelancing"})
        ensure_enrollment(fatmata, data_course, "in_progress", {"Introduction to Data Analysis"})
        ensure_enrollment(abdul, python_course, "in_progress")
        ensure_enrollment(abdul, web_course, "in_progress", {"Introduction to Web Development", "Getting Started with HTML"})
        ensure_enrollment(isata, freelancing_course, "completed", {"Introduction to Freelancing", "Identifying Your Marketable Skills"})
        ensure_enrollment(joseph, freelancing_course, "in_progress")

        # --- Portfolios ---------------------------------------------------------------
        ensure_portfolio(
            aminata,
            "Frontend Developer & UI Enthusiast",
            "I build clean, responsive websites and am developing my skills in user-interface design. I enjoy turning ideas into simple, usable web pages.",
            [
                (
                    "Community Library Website",
                    "A responsive informational website built for a local community library, including a catalogue page and event listings.",
                    date(2026, 6, 15),
                    None,
                ),
            ],
        )
        ensure_portfolio(
            mohamed,
            "Graphic Designer | Branding & Social Media Graphics",
            "I design logos, flyers, and social media graphics for small businesses and community organisations across Sierra Leone.",
            [
                (
                    "GreenLeaf Agribusiness Brand Refresh",
                    "Designed a new logo and a set of social media templates for an agribusiness client.",
                    date(2026, 7, 2),
                    None,
                ),
                (
                    "Training Programme Promotional Flyer",
                    "Created a promotional flyer used to advertise a digital skills training programme.",
                    date(2026, 7, 20),
                    None,
                ),
            ],
        )
        ensure_portfolio(
            fatmata,
            "Data Analyst | Excel & Reporting",
            "I help small organisations make sense of their data through clear spreadsheets, summaries, and simple visualisations.",
            [
                (
                    "Monthly Sales Tracker",
                    "Built an Excel workbook with automated summaries and charts for tracking monthly sales performance.",
                    date(2026, 5, 30),
                    None,
                ),
            ],
        )

        # --- Freelance opportunities --------------------------------------------------
        opp_uiux, _ = get_or_create_opportunity(
            samuel,
            "Design a Mobile App Wireframe for a Ride-Hailing Startup",
            "We need a set of wireframes and a clickable prototype for a new ride-hailing mobile app, covering the booking flow, driver matching screen, and payment confirmation.",
            "UI/UX Design",
            4500,
            date(2026, 9, 30),
        )
        opp_data, _ = get_or_create_opportunity(
            rugiatu,
            "Analyse Farm Sales Data and Build a Reporting Dashboard",
            "Looking for a data analyst to clean two years of farm sales records and build a simple dashboard summarising revenue by crop and by month.",
            "Data Analysis",
            3200,
            date(2026, 10, 15),
        )
        opp_content, _ = get_or_create_opportunity(
            precious,
            "Write Website Copy for a New Consulting Firm",
            "We need engaging, professional website copy for our homepage, services page, and about page.",
            "Content Writing",
            1500,
            date(2026, 9, 10),
        )
        opp_social, _ = get_or_create_opportunity(
            precious,
            "Manage Social Media Accounts for One Month",
            "Seeking a social media manager to plan and schedule content across Facebook and Instagram for a one-month trial period.",
            "Digital Marketing",
            2000,
            date(2026, 9, 25),
        )
        opp_video, _ = get_or_create_opportunity(
            samuel,
            "Edit Highlight Reel from Community Tech Event",
            "We recorded four hours of footage from our tech meet-up and need a five-minute highlight video edited with captions and background music.",
            "Video Editing",
            1200,
            date(2026, 9, 5),
        )
        opp_software, _ = get_or_create_opportunity(
            samuel,
            "Build a Simple Attendance Tracking Application",
            "We need a lightweight web application for tracking attendance at our weekly coding meet-ups, with an admin login and CSV export.",
            "Software Development",
            5000,
            date(2026, 11, 1),
        )
        # Close one older opportunity to reflect a completed engagement.
        opp_flyer = db.session.scalar(
            db.select(FreelanceOpportunity).filter_by(
                title="Design a Professional Promotional Flyer for a Training Programme"
            )
        )
        if opp_flyer is not None:
            opp_flyer.status = "closed"

        # --- Job applications -----------------------------------------------------
        ensure_application(
            opp_uiux, aminata,
            "I have been studying UI/UX design and would love the opportunity to design this wireframe and prototype for your team.",
            4200, "under_review",
        )
        ensure_application(
            opp_data, fatmata,
            "I have experience cleaning and summarising sales data in Excel and can build the dashboard you described.",
            3000, "accepted",
        )
        ensure_application(
            opp_content, isata,
            "I specialise in clear, persuasive website copy and would enjoy writing for your consulting firm.",
            1400, "pending",
        )
        ensure_application(
            opp_social, joseph,
            "I have managed social media pages for local community groups and can put together a content plan for your trial month.",
            1800, "pending",
        )
        ensure_application(
            opp_video, joseph,
            "I can turn your event footage into a polished highlight reel with captions within one week.",
            1100, "rejected",
        )
        ensure_application(
            opp_software, abdul,
            "I am building my software development skills through the platform's courses and would welcome the chance to build this tracker.",
            4500, "pending",
        )

        # --- Mentorships -------------------------------------------------------------
        ensure_mentorship(
            aminata, mariama,
            "I'd like guidance on improving my UI/UX design skills and getting feedback on my wireframes.",
            "accepted", with_goals=True,
        )
        ensure_mentorship(
            fatmata, alhaji,
            "I would appreciate mentorship on building dashboards and improving my Excel and data analysis skills.",
            "accepted", with_goals=True,
        )
        ensure_mentorship(
            isata, sallay,
            "I'm interested in mentorship on digital marketing and growing a freelance writing career.",
            "pending",
        )
        ensure_mentorship(
            joseph, sallay,
            "Could you mentor me on social media management and building a client base?",
            "rejected",
        )

        db.session.commit()

        summary = {
            "users": db.session.scalar(db.select(db.func.count(User.id))),
            "skills": db.session.scalar(db.select(db.func.count(Skill.id))),
            "courses": db.session.scalar(db.select(db.func.count(Course.id))),
            "lessons": db.session.scalar(db.select(db.func.count(Lesson.id))),
            "enrollments": db.session.scalar(db.select(db.func.count(Enrollment.id))),
            "portfolios": db.session.scalar(db.select(db.func.count(Portfolio.id))),
            "opportunities": db.session.scalar(db.select(db.func.count(FreelanceOpportunity.id))),
            "applications": db.session.scalar(db.select(db.func.count(JobApplication.id))),
            "mentorship_requests": db.session.scalar(db.select(db.func.count(MentorshipRequest.id))),
            "mentorships": db.session.scalar(db.select(db.func.count(Mentorship.id))),
            "notifications": db.session.scalar(db.select(db.func.count(Notification.id))),
        }
        print("Demo data seeded. Current totals:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        print(f"\nAll newly created demo accounts use the password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    run()
