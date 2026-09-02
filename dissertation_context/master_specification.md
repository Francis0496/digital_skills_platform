MASTER DEVELOPMENT SPECIFICATION
Digital Skills and Freelancing Platform for Youth in Sierra Leone
Case Study: Youth in Freetown

Project-Based Undergraduate Dissertation
Faculty of Information Systems & Technology
B.Sc. (Hons.) Information Technology

Purpose: Authoritative specification for incremental SDLC development with Codex

# 1. Purpose and Authority
This document is the single technical source of truth for the design and incremental development of the Digital Skills and Freelancing Platform. It translates the approved project direction into implementable software requirements, architecture, database rules, user experience requirements, testing criteria, deployment guidance, and Codex working instructions.
The application is a fully functional web-based prototype. The dissertation remains project-based: research and literature support problem definition, requirements, design choices, and evaluation, while the principal artefact is the working information system.
Where this specification conflicts with an ad hoc coding suggestion, this specification takes precedence unless the project owner explicitly approves a change.
# 2. Project Vision and Problem Definition
## 2.1 Vision
To provide a localised web platform through which youth in Freetown can develop practical digital skills, create professional profiles and portfolios, access freelance opportunities, receive mentorship, and progress from learning toward income-generating digital work.
## 2.2 Problem Definition
Young people seeking digital work often use disconnected services for learning, portfolio building, mentorship, and opportunity discovery. International freelance marketplaces also assume a level of experience, profile maturity, and market readiness that can be difficult for beginners. The proposed platform addresses this fragmented pathway by integrating skills development and freelancing support in one system.
## 2.3 Aim
To design and develop a web-based Digital Skills and Freelancing Platform that supports digital skills development and facilitates access to freelancing opportunities for youth in Freetown, Sierra Leone.
## 2.4 Development Objectives
Analyse and document the system requirements and business rules for digital learning, portfolios, freelancing, mentorship, and administration.
Design the application architecture, database, interfaces, access-control model, and system workflows.
Implement secure user authentication and role-based access for freelancers/learners, mentors, clients, and administrators.
Implement digital learning, profile and portfolio management, freelance opportunities and applications, mentorship, notifications, and administrative management.
Test the completed prototype against defined functional and non-functional requirements.
Deploy and document a working prototype suitable for demonstration and dissertation evaluation.
# 3. Scope and Prototype Boundaries
## 3.1 In Scope
Registration, login, logout, password hashing, account status, and role-based access control.
Freelancer/learner, mentor, client, and administrator roles.
Professional profiles and digital skills.
Course categories, courses, lessons, enrolment, lesson completion, and progress tracking.
Freelancer portfolio and portfolio project management.
Freelance opportunity creation, browsing, searching/filtering, application submission, and application status management.
Mentor directory, mentorship requests, acceptance/rejection, and active mentorship records.
In-application notifications for important events.
Administrative dashboard, user management, course management, opportunity oversight, mentorship oversight, and basic platform statistics.
Responsive web interface and complete prototype testing.
## 3.2 Out of Scope for Initial Prototype
Native Android or iOS applications.
Direct integration with Upwork, Fiverr, Freelancer, or PeoplePerHour.
Credit-card, mobile-money, escrow, or international payment processing.
Real-time video conferencing.
Enterprise microservices or distributed infrastructure.
AI-based job matching or automated recommendation engines.
Long-term measurement of employment outcomes.
# 4. Approved Technology Stack
SQLite is intentionally selected for the prototype. The schema should remain portable enough to migrate to PostgreSQL for larger production deployment.
# 5. SDLC Methodology
The project will use an iterative SDLC. Each phase is documented, but development occurs incrementally so that modules can be designed, implemented, tested, reviewed, and integrated before the next module begins.
# 6. System Actors and Role Responsibilities
# 7. Functional Requirements
# 8. Non-Functional Requirements
# 9. Business Rules
BR01: Every account must use a unique email address.
BR02: Passwords are never stored as plain text.
BR03: Every user has one primary role.
BR04: Protected actions require authentication and server-side authorization.
BR05: Deactivated users cannot use protected application functionality.
BR06: A learner cannot enrol in the same course more than once.
BR07: Lesson progress can only be recorded for an enrolment owned by the current learner.
BR08: Users can only modify profile, portfolio, application, opportunity, or mentorship records they own or are authorized to manage.
BR09: Only clients and authorized administrators can create freelance opportunities.
BR10: Only freelancers can apply for freelance opportunities.
BR11: A freelancer cannot submit duplicate applications for the same opportunity.
BR12: Closed or expired opportunities cannot accept new applications.
BR13: Application statuses are Pending, Under Review, Accepted, or Rejected.
BR14: Only freelancers can initiate mentorship requests.
BR15: A mentorship becomes active only after mentor acceptance.
BR16: Administrators may deactivate accounts and moderate managed platform records.
BR17: Administrative access is never granted solely by a client-supplied form value or URL parameter.
BR18: Referential integrity must be preserved when deleting or deactivating related records.
# 10. Database Design Specification
The database is relational. SQLAlchemy models must define explicit foreign keys, relationships, constraints, timestamps where useful, and ownership rules. Migration scripts must accompany schema changes.
# 11. Relationship and Data Integrity Rules
Role has many Users; each User has one primary Role.
User and Skill are many-to-many through UserSkill.
CourseCategory has many Courses; Course has many Lessons.
User and Course are many-to-many through Enrollment.
LessonProgress belongs to an Enrollment and Lesson.
A freelancer has at most one primary Portfolio, which contains many PortfolioProjects.
A Client/User can own many FreelanceOpportunities.
An Opportunity can receive many JobApplications; a Freelancer can submit many applications, but only one per opportunity.
A Mentor/User has at most one MentorProfile.
MentorshipRequest connects one freelancer and one mentor.
Notification belongs to one User.
Deletion behaviour must avoid orphaned records. Prefer controlled deletion or cascading only where data loss is safe and intentional.
# 12. Application Architecture
Use a modular monolith with three logical layers: presentation, application/business logic, and data access. Flask Blueprints divide functional areas without introducing unnecessary distributed-system complexity.
Browser → Jinja2/HTML/Tailwind/JavaScript → Flask Routes/Services → SQLAlchemy → SQLite
## 12.1 Required Repository Structure
digital_skills_platform/
├── AGENTS.md
├── PROJECT_SPECIFICATION.md
├── DATABASE_DESIGN.md
├── UI_UX_SPECIFICATION.md
├── TESTING_PLAN.md
├── REQUIREMENTS_TRACEABILITY.md
├── DECISIONS.md
├── README.md
├── .env.example
├── requirements.txt
├── config.py
├── run.py
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   ├── auth/
│   ├── main/
│   ├── users/
│   ├── courses/
│   ├── portfolio/
│   ├── opportunities/
│   ├── mentorship/
│   ├── notifications/
│   ├── admin/
│   ├── templates/
│   └── static/
├── migrations/
├── tests/
└── instance/
# 13. Route and Module Architecture
Exact route names may evolve during implementation, but route ownership, authorization, and user workflow must remain consistent with this specification.
# 14. UI/UX Specification
## 14.1 Public Pages
Home
About
Course catalogue
Course details
Freelance opportunity catalogue
Opportunity details
Mentor directory
Mentor profile
Login
Registration
## 14.2 Freelancer/Learner Pages
Dashboard
Profile
Skills
My Courses
Course/Lesson Learning View
Learning Progress
Portfolio
Portfolio Project Form
Browse Opportunities
My Applications
Mentor Directory
Mentorship Requests
Notifications
Account Settings
## 14.3 Mentor Pages
Mentor Dashboard
Mentor Profile
Pending Mentorship Requests
My Mentees
Notifications
## 14.4 Client Pages
Client Dashboard
Client Profile
Post Opportunity
My Opportunities
Opportunity Applications
Applicant Profile/Portfolio
Notifications
## 14.5 Administrator Pages
Admin Dashboard
Users
Roles/Account Status
Skills
Course Categories
Courses
Lessons
Opportunities
Applications Oversight
Mentors
Mentorship Records
Platform Statistics
## 14.6 Page-Level UX Rules
Every protected page must show navigation appropriate to the current role.
Forms must show field-level validation errors and preserve safe submitted values after validation failure.
Empty states must explain what the user can do next.
Destructive actions require clear confirmation.
Success and error feedback should use Flask flash messages or an equivalent consistent pattern.
Layouts must be responsive and keyboard-accessible where practical.
Do not expose controls that the current role cannot use, but always enforce authorization on the server even if a control is hidden.
# 15. Access Control Matrix
# 16. Validation and Security Requirements
Use Flask-WTF CSRF protection for state-changing HTML forms.
Hash passwords using Werkzeug. Never log or display passwords.
Validate email uniqueness at both application and database levels.
Validate ownership and role on every create, update, delete, status-change, and protected view route.
Do not rely on client-side validation for security.
Use safe file names and an allowlist for uploaded file types; enforce reasonable size limits.
Do not execute uploaded content.
Use environment variables for secrets and deployment configuration; do not commit secrets.
Use a strong SECRET_KEY outside development.
Prevent open redirects after login by validating next destinations.
Use parameterized ORM operations rather than string-built SQL.
Return 403 for unauthorized operations, 404 where appropriate, and custom 404/500 pages for user-facing errors.
Protect against duplicate enrolments and applications with database constraints as well as application checks.
Do not grant administrator role through public registration.
Seed/demo credentials must never be production credentials.
# 17. File Upload Requirements
Profile images and portfolio project images may be supported.
For the prototype, local upload storage is acceptable if deployment supports persistent files; otherwise use a clearly documented external storage option.
Allowed extensions should be restricted to common safe image formats.
Generated stored filenames should avoid collisions and path traversal.
Database records should store file references, not binary image content.
Missing or deleted files should degrade gracefully to default placeholders.
# 18. Notification Events
# 19. Error Handling and Logging
Provide user-friendly 403, 404, and 500 pages.
Validation failures must not create partial records.
Database transactions should roll back on failed multi-step operations.
Log application errors without logging passwords or sensitive secrets.
Development debugging may be enabled locally only; production deployment must disable debug mode.
Unexpected exceptions should be captured in logs and converted to safe user-facing feedback.
# 20. Testing Strategy
## 20.1 Definition of Done for Any Feature
Requirement and business rule are understood.
Database changes are migrated.
Authorization and validation are implemented.
Happy path works.
Important failure/edge paths work.
Automated tests are added or updated.
Existing tests still pass.
UI is responsive and gives clear feedback.
Documentation/traceability is updated.
No unrelated working functionality is removed.
# 21. Incremental Development Plan
# 22. Acceptance Criteria by Increment
## Increment 1
☐ Application starts through the application factory without errors.
☐ Development/test configuration is separated from secrets.
☐ SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, and pytest are initialized.
☐ Base template and responsive navigation shell render.
☐ Database migration workflow functions.
☐ 403/404/500 handlers exist.
☐ Initial tests pass.
## Increment 2
☐ User can register with a unique email and permitted public role.
☐ Password is hashed.
☐ Valid active user can log in and log out.
☐ Invalid credentials are rejected safely.
☐ Inactive user cannot use protected application functions.
☐ Role-specific protected routes reject unauthorized roles.
☐ Administrator cannot be self-created through public registration.
☐ Authentication and authorization tests pass.
## Increment 3
☐ Users can view and edit their own profiles.
☐ Freelancers can add/remove approved skills without duplicates.
☐ Mentor profile stores expertise and availability.
☐ Clients can maintain relevant profile information.
☐ Users cannot edit another user's private profile data.
☐ Profile tests pass.
## Increment 4
☐ Admin can manage categories, courses, and lessons.
☐ Only published courses appear in public/learner catalogue.
☐ Learner can enrol once per course.
☐ Enrolled learner can access lessons.
☐ Lesson completion is stored once and progress is calculated correctly.
☐ Unauthorized users cannot alter course content or another learner's progress.
☐ Learning tests pass.
## Increment 5
☐ Freelancer can create a portfolio and project entries.
☐ Freelancer can edit/delete only owned projects.
☐ Portfolio supports project title, description, link, image reference, and completion date as applicable.
☐ Authorized viewers can view portfolio presentation.
☐ Portfolio tests pass.
## Increment 6
☐ Client can create/edit/close only owned opportunities.
☐ Active opportunities are discoverable.
☐ Closed/expired opportunities do not accept new applications.
☐ Search/filter functionality returns appropriate opportunities.
☐ Marketplace tests pass.
## Increment 7
☐ Freelancer can submit one application per active opportunity.
☐ Duplicate applications are prevented by code and database constraint.
☐ Client can see applications only for owned opportunities.
☐ Client can update allowed statuses.
☐ Freelancer can track application status.
☐ Relevant notifications are generated.
☐ Application tests pass.
## Increment 8
☐ Freelancer can browse mentor profiles.
☐ Freelancer can submit a mentorship request.
☐ Mentor can see requests addressed to them.
☐ Mentor can accept or reject a pending request.
☐ Acceptance creates or activates the mentorship relationship without duplication.
☐ Relevant notifications are generated.
☐ Mentorship tests pass.
## Increment 9
☐ Administrator dashboard shows accurate core counts.
☐ Administrator can search/view and activate/deactivate users.
☐ Administrator can manage defined content and oversight functions.
☐ Users can view and mark their own notifications as read.
☐ Non-admin users cannot access admin functions.
☐ Admin and notification tests pass.
## Increment 10
☐ Full automated test suite passes.
☐ Manual system test checklist is completed.
☐ Role authorization matrix is verified.
☐ Responsive layouts are checked at representative widths.
☐ Demo data is safe and reproducible.
☐ Deployment starts successfully with debug disabled.
☐ User manual and dissertation screenshots/evidence are captured.
☐ Known limitations are documented.
# 23. Codex Working Rules (for AGENTS.md)
Treat PROJECT_SPECIFICATION.md and this master specification as authoritative.
Do not change the approved stack or architecture without explicit approval.
Use the Flask application factory pattern and Blueprints.
Do not place the complete application in a single app.py file.
Use SQLAlchemy models and migrations. Avoid raw SQL unless specifically justified.
Use Flask-Login for session authentication.
Use Flask-WTF/CSRF for state-changing HTML forms.
Enforce role and ownership authorization on the server.
Never store plaintext passwords or commit secrets.
Inspect existing models, routes, templates, migrations, and tests before modifying a module.
Preserve existing working functionality while implementing a new increment.
Make the smallest coherent change that completes the approved increment.
Do not invent features outside the specification.
Do not silently rename database fields or routes used by existing code without updating all dependencies and tests.
Create a migration for every schema change after migrations are established.
Run the existing test suite before and after meaningful changes.
Add tests for new business rules, authorization, and failure paths.
Report changed files, migrations, tests run, test results, and any unresolved issue after each increment.
Do not mark an increment complete until every acceptance criterion is satisfied or explicitly documented as blocked.
Ask for approval before major refactoring, new external services, or changes that alter scope.
Keep code readable and dissertation-friendly: clear names, concise comments for non-obvious logic, and modular organization.
# 24. Reusable Codex Increment Prompt Template
You are implementing [INCREMENT NAME] of the Digital Skills and Freelancing Platform.

Authoritative sources:
1. AGENTS.md
2. PROJECT_SPECIFICATION.md
3. DATABASE_DESIGN.md
4. UI_UX_SPECIFICATION.md
5. TESTING_PLAN.md
6. REQUIREMENTS_TRACEABILITY.md

Before coding:
- Inspect the existing repository, relevant models, routes, templates, migrations, and tests.
- State briefly what already exists and what must change for this increment.
- Do not change the approved technology stack or unrelated modules.

Implementation requirements:
[INSERT APPROVED REQUIREMENTS FOR THIS INCREMENT]

Acceptance criteria:
[INSERT CHECKLIST FOR THIS INCREMENT]

Engineering rules:
- Preserve existing working functionality.
- Enforce authentication, role authorization, ownership, validation, and CSRF where applicable.
- Use SQLAlchemy and migrations for schema changes.
- Add or update automated tests for happy paths, important failures, and unauthorized access.
- Do not add features outside the approved scope.

Verification:
- Run the relevant tests, then the full test suite.
- Fix regressions caused by this increment.
- Do not claim completion if tests or acceptance criteria fail.

At completion, report:
1. Summary of implementation.
2. Files created/changed.
3. Database migration(s).
4. Tests added/changed.
5. Commands/tests executed and results.
6. Acceptance criteria status.
7. Known limitations or decisions requiring approval.
# 25. Git and Increment Control
Create a clean commit at the end of each verified increment.
Use descriptive commit messages such as: feat(auth): implement registration and role access.
Do not combine unrelated features into the same commit.
Tag or note stable milestones where useful.
Before beginning the next increment, confirm the previous increment's tests pass.
Keep generated secrets, virtual environments, local databases, cache files, and uploads out of Git unless intentionally included as safe demo fixtures.
# 26. Deployment Strategy
Develop locally with SQLite and environment-based configuration.
Select a Python-compatible hosting environment for the final prototype.
Confirm whether persistent SQLite storage and uploaded files are supported by the chosen host.
If the host uses ephemeral storage, either select a host with persistent disk or document/migrate storage appropriately.
Use production SECRET_KEY and environment variables.
Disable debug mode.
Run migrations during deployment.
Seed only non-sensitive demonstration data.
Verify login, role access, courses, opportunities, applications, mentorship, notifications, and admin workflows after deployment.
# 27. Requirements Traceability Model
# 28. Development Decision Log
# 29. Dissertation Mapping
# 30. Documentation Artefacts to Maintain in Repository
# 31. Immediate Next Action
Do not ask Codex to build the full platform yet. First create the repository documentation set from this master specification. Then execute Increment 1 only. Verify the foundation, commit it, and proceed to Increment 2 after the acceptance criteria pass.
The recommended working cycle is: Specification → Codex Increment → Tests → Review → Commit → Dissertation Evidence → Next Increment.
# 32. Source Alignment Notes
This specification preserves the core proposal concept: a web-based Digital Skills and Freelancing Platform combining digital skills training, user profiles/portfolios, mentorship, freelance opportunities, and administration. It also follows the official IPAM/FIST project-dissertation structure, which expects problem definition and scope, methodology/literature, analysis and design, implementation results, system testing, and final evaluation. Harvard referencing should be used in the dissertation.
The detailed engineering rules, database constraints, route structure, test strategy, and Codex workflow are development specifications derived to operationalise those approved project requirements. They are not claims copied from the source documents.

[TABLE]
Layer/Concern | Approved Technology | Reason
Language | Python | Primary application language and strong Flask ecosystem.
Backend | Flask | Lightweight, suitable for a functional prototype and modular development.
Templates | Jinja2 | Server-rendered UI integrates directly with Flask.
Frontend | HTML5 + JavaScript | Accessible, simple, and sufficient for required interactivity.
Styling | Tailwind CSS | Responsive and consistent interface development.
ORM | Flask-SQLAlchemy / SQLAlchemy | Relational modelling and maintainable data access.
Database | SQLite | Appropriate for the prototype, portable, relational, and low administration.
Authentication | Flask-Login | Session-based authentication suited to Jinja/Flask application.
Forms/CSRF | Flask-WTF / WTForms | Server-side validation and CSRF protection.
Passwords | Werkzeug security helpers | Secure password hashing and verification.
Migrations | Flask-Migrate / Alembic | Controlled database schema evolution.
Testing | pytest | Automated unit, route, authorization, and integration tests.
Version Control | Git + GitHub | Incremental development, history, rollback, and evidence.
[/TABLE]


[TABLE]
Phase | Primary Outputs
1. Planning | Problem, objectives, feasibility, scope, stack, risks, work plan.
2. Requirements Analysis | Actors, functional requirements, non-functional requirements, business rules, acceptance criteria.
3. System Design | Architecture, ERD, database schema, use cases, workflows, interface design, permissions.
4. Development | Incremental implementation using approved Flask architecture.
5. Testing | Automated and manual tests, defect correction, usability checks.
6. Deployment | Demo data, configuration, hosting, deployment verification.
7. Evaluation/Maintenance | Objective assessment, limitations, improvements, future work.
[/TABLE]


[TABLE]
Role | Primary Responsibilities
Freelancer/Learner | Learn skills, maintain profile and portfolio, browse/apply for opportunities, request mentorship, track progress and applications.
Mentor | Maintain mentor profile, receive and respond to mentorship requests, manage mentees.
Client/Opportunity Provider | Maintain client profile, post/manage opportunities, review applicants and update application status.
Administrator | Manage platform users, content, courses, skills, opportunities, mentors, records, and statistics.
[/TABLE]


[TABLE]
ID | Requirement | Specification
FR01 | Registration | The system shall allow eligible users to register using a unique email address and valid required information.
FR02 | Authentication | The system shall allow active users to log in and log out securely.
FR03 | Role-Based Access | The system shall authorize protected actions according to assigned role.
FR04 | Profile Management | Users shall create and update role-appropriate profile information.
FR05 | Skills Management | Freelancers shall associate digital skills and proficiency levels with their profiles.
FR06 | Course Management | Administrators shall create, edit, publish/unpublish, and manage courses and categories.
FR07 | Lesson Management | Administrators shall create and order lessons belonging to courses.
FR08 | Course Browsing | Users shall browse published courses and view course details.
FR09 | Course Enrolment | Authenticated learners shall enrol once in an available course.
FR10 | Learning Progress | Learners shall mark lessons complete and view calculated course progress.
FR11 | Portfolio Management | Freelancers shall create and maintain a professional portfolio.
FR12 | Portfolio Projects | Freelancers shall add, edit, and remove projects from their own portfolios.
FR13 | Opportunity Management | Clients shall create, edit, close, and manage their own freelance opportunities.
FR14 | Opportunity Discovery | Freelancers shall browse, search, and filter active opportunities.
FR15 | Applications | Freelancers shall apply once per active opportunity with a cover message and proposed amount.
FR16 | Application Review | Clients shall review applicants and update application status.
FR17 | Application Tracking | Freelancers shall view the current status of submitted applications.
FR18 | Mentor Directory | Freelancers shall browse mentor profiles and expertise.
FR19 | Mentorship Requests | Freelancers shall submit mentorship requests to mentors.
FR20 | Mentorship Response | Mentors shall accept or reject pending requests.
FR21 | Mentorship Records | The system shall maintain active mentorship relationships.
FR22 | Notifications | The system shall create in-app notifications for defined important events.
FR23 | Admin Dashboard | Administrators shall view core platform counts and management shortcuts.
FR24 | User Administration | Administrators shall search, inspect, activate/deactivate, and manage users.
FR25 | Content Administration | Administrators shall manage skills, courses, lessons, and appropriate platform content.
FR26 | Platform Oversight | Administrators shall monitor opportunities, applications, mentors, and mentorship records.
[/TABLE]


[TABLE]
ID | Quality | Requirement
NFR01 | Usability | Navigation and forms shall be understandable and consistent for first-time users.
NFR02 | Responsiveness | Core pages shall work on desktop, laptop, tablet, and smartphone widths.
NFR03 | Security | Passwords shall be hashed; protected routes require authentication; authorization is enforced server-side; forms use CSRF protection.
NFR04 | Data Integrity | Unique constraints, foreign keys, validation, and application rules shall prevent invalid or duplicate records.
NFR05 | Performance | Normal prototype interactions shall complete without unnecessary delay under expected demonstration load.
NFR06 | Reliability | Valid operations shall behave consistently and failures shall return useful error feedback without corrupting data.
NFR07 | Maintainability | The application shall use an application factory, Blueprints, models, reusable templates, and clear module separation.
NFR08 | Portability | Configuration shall separate environment-specific values and permit later database migration.
NFR09 | Compatibility | The UI shall support current Chrome, Edge, and Firefox browsers.
NFR10 | Testability | Core business rules, authentication, authorization, and routes shall have repeatable tests.
[/TABLE]


[TABLE]
Entity | Minimum Fields/Constraints | Key Relationships
Role | id PK; name UNIQUE NOT NULL | 1:M User
User | id PK; full_name; email UNIQUE; password_hash; role_id FK; phone; location; bio; profile_image; is_active; created_at | M:1 Role; M:M Skill; related role data
Skill | id PK; name UNIQUE; description | M:M User
UserSkill | id PK; user_id FK; skill_id FK; proficiency_level; UNIQUE(user_id,skill_id) | Join User/Skill
CourseCategory | id PK; name UNIQUE; description | 1:M Course
Course | id PK; category_id FK; title; description; difficulty_level; image; is_published; created_at | M:1 Category; 1:M Lesson; M:M User via Enrollment
Lesson | id PK; course_id FK; title; content; video_url; lesson_order; created_at | M:1 Course
Enrollment | id PK; user_id FK; course_id FK; enrolled_at; completion_status; UNIQUE(user_id,course_id) | Join User/Course
LessonProgress | id PK; enrollment_id FK; lesson_id FK; completed; completed_at; UNIQUE(enrollment_id,lesson_id) | M:1 Enrollment/Lesson
Portfolio | id PK; user_id FK UNIQUE; title; description | 1:1 User; 1:M Project
PortfolioProject | id PK; portfolio_id FK; title; description; project_image; project_url; completion_date | M:1 Portfolio
FreelanceOpportunity | id PK; client_id FK; title; description; category; budget; deadline; status; created_at | M:1 Client; 1:M Application
JobApplication | id PK; opportunity_id FK; freelancer_id FK; cover_message; proposed_amount; status; submitted_at; UNIQUE(opportunity_id,freelancer_id) | M:1 Opportunity/Freelancer
MentorProfile | id PK; user_id FK UNIQUE; professional_title; expertise; experience; availability | 1:1 Mentor User
MentorshipRequest | id PK; freelancer_id FK; mentor_id FK; message; status; requested_at | M:1 users
Mentorship | id PK; freelancer_id FK; mentor_id FK; start_date; status | M:1 users
Notification | id PK; user_id FK; message; notification_type; is_read; created_at | M:1 User
[/TABLE]


[TABLE]
Blueprint | Representative Routes | Purpose
auth | /register, /login, /logout | Authentication and account entry.
main | /, /about, /courses, /opportunities, /mentors | Public pages and discovery.
users | /dashboard, /profile, /skills | Role dashboard and profile management.
courses | /courses/<id>, /courses/<id>/enrol, /lessons/<id>, /progress | Learning workflows.
portfolio | /portfolio, /portfolio/projects/new, /portfolio/projects/<id>/edit | Portfolio ownership and projects.
opportunities | /opportunities, /opportunities/new, /opportunities/<id>, /opportunities/<id>/apply, /applications | Marketplace and applications.
mentorship | /mentors, /mentors/<id>, /mentors/<id>/request, /mentorship/requests | Mentorship workflows.
notifications | /notifications, /notifications/<id>/read | In-app notifications.
admin | /admin, /admin/users, /admin/courses, /admin/opportunities, /admin/mentorships | Administration and oversight.
[/TABLE]


[TABLE]
Function | Freelancer | Mentor | Client | Administrator
Login | Yes | Yes | Yes | Yes
Manage own profile | Yes | Yes | Yes | Yes
Manage skills | Yes | Optional | Optional | Yes
Enrol/track learning | Yes | No | No | Oversight
Manage own portfolio | Yes | No | No | Oversight
Post opportunities | No | No | Yes | Yes
Apply to opportunities | Yes | No | No | No
Review own opportunity applicants | No | No | Yes | Yes
Request mentorship | Yes | No | No | No
Respond to mentorship requests | No | Yes | No | Oversight
Manage users/content | No | No | No | Yes
View platform statistics | No | No | No | Yes
[/TABLE]


[TABLE]
Event | Recipient | Example
Course enrolment | Learner | You enrolled in a course.
Application submitted | Client | A freelancer applied to your opportunity.
Application status changed | Freelancer | Your application status was updated.
Mentorship request submitted | Mentor | You received a mentorship request.
Mentorship response | Freelancer | Your mentorship request was accepted/rejected.
Administrative action where useful | Affected user | Your account/status was updated.
[/TABLE]


[TABLE]
Test Type | Purpose
Unit tests | Validate isolated helpers, model rules, calculations, and services.
Model/database tests | Validate constraints, relationships, and ownership assumptions.
Authentication tests | Registration, login, logout, inactive account behavior.
Authorization tests | Verify each role cannot access unauthorized actions.
Route/form tests | Validate success paths, invalid input, CSRF-aware workflows, redirects, and flash feedback.
Integration tests | Verify modules work together, e.g., opportunity → application → notification.
System tests | Run end-to-end prototype scenarios against requirements.
Usability tests | Assess navigation, clarity, responsiveness, and task completion with selected users.
[/TABLE]


[TABLE]
Increment | Focus | Deliverables
Increment 1 | Foundation | Repository, virtual environment, application factory, configuration, extensions, database connection, migrations, Tailwind integration, base templates, pytest setup, error handlers, documentation skeleton.
Increment 2 | Authentication and RBAC | Roles, users, registration, login/logout, password hashing, inactive accounts, protected routes, role dashboards, authorization decorators/helpers.
Increment 3 | Profiles and Skills | Role-appropriate profiles, freelancer skills, mentor profile, client profile, profile editing, optional profile image.
Increment 4 | Digital Learning | Course categories, courses, lessons, publishing, enrolment, lesson completion, progress calculation, admin course management.
Increment 5 | Portfolio | Portfolio creation, project CRUD, image/link support, public/authorized portfolio view.
Increment 6 | Freelance Marketplace | Opportunity CRUD, ownership, active/closed state, catalogue, details, search/filtering.
Increment 7 | Applications | Application submission, duplicate prevention, client review, status changes, freelancer tracking, notifications.
Increment 8 | Mentorship | Mentor directory, request submission, accept/reject, active mentorship records, notifications.
Increment 9 | Administration and Notifications | Admin statistics, user management, moderation/oversight, notification centre and read status.
Increment 10 | Hardening and Deployment | Full regression tests, security/authorization review, responsive polish, demo data, usability testing, deployment, user manual, screenshots and dissertation evidence.
[/TABLE]


[TABLE]
Requirement | Module | Implementation Evidence | Test Evidence | Dissertation Evidence
FR01-FR03 | Authentication/RBAC | Routes, forms, User/Role models | AUTH test cases | Ch. 4 analysis; Ch. 5 results
FR04-FR05 | Profiles/Skills | Profile and UserSkill implementation | PROFILE tests | Ch. 4 design; Ch. 5 screenshots
FR06-FR10 | Digital Learning | Course/Lesson/Enrollment/Progress | COURSE tests | Ch. 4 ERD; Ch. 5 results
FR11-FR12 | Portfolio | Portfolio and project CRUD | PORTFOLIO tests | Ch. 5 feature evidence
FR13-FR17 | Freelancing | Opportunity/Application workflows | JOB tests | Ch. 4 use cases; Ch. 5 results
FR18-FR21 | Mentorship | Mentor/request/relationship workflows | MENTOR tests | Ch. 5 results
FR22 | Notifications | Notification events/read state | NOTIFICATION tests | Ch. 5 results
FR23-FR26 | Administration | Admin dashboard/management | ADMIN tests | Ch. 5 results
[/TABLE]


[TABLE]
Decision | Selected Option | Rationale
ADR-001 | Project-based dissertation | The principal output is a working information system documented through analysis, design, implementation, and testing.
ADR-002 | Iterative SDLC | Supports controlled incremental delivery and testing while preserving formal SDLC stages.
ADR-003 | Flask | Appropriate lightweight framework for the functional prototype.
ADR-004 | SQLite | Low-administration relational database appropriate to prototype scope.
ADR-005 | SQLAlchemy | Structured relational modelling and easier future database portability.
ADR-006 | Flask-Login | Suitable session authentication for server-rendered Flask/Jinja application.
ADR-007 | Tailwind CSS | Responsive UI development with consistent reusable styling.
ADR-008 | Modular monolith | Sufficient separation and maintainability without unnecessary microservice complexity.
ADR-009 | In-app notifications | Meets prototype needs without requiring email/SMS infrastructure.
ADR-010 | No payment integration | Avoids regulatory/security complexity outside dissertation scope.
[/TABLE]


[TABLE]
Dissertation Section | Development Evidence
Chapter One: Introduction | Problem, aim, objectives, significance, technology, organisation.
Chapter Two: Problem Definition and Scope | Existing fragmented process, detailed problem, system boundaries, user groups.
Chapter Three: Literature Review/Methodology | Related platforms/literature; SDLC options; iterative SDLC selection and justification.
Chapter Four: Analysis and Design | Requirements, business rules, use cases, architecture, ERD, schema, permissions, interface design.
Chapter Five: Results and Discussion | Implemented modules, screenshots, deployment issues, test results, objective evidence.
Chapter Six: Summary, Conclusion and Recommendations | Achievement against objectives, constraints, limitations, conclusions, future enhancements.
Appendices | User manual, schema, test scripts/data, selected source code, supporting instruments if used.
[/TABLE]


[TABLE]
File | Purpose
AGENTS.md | Mandatory Codex engineering and repository rules.
PROJECT_SPECIFICATION.md | Approved product vision, scope, requirements, and business rules.
DATABASE_DESIGN.md | Tables, fields, constraints, relationships, deletion rules, ERD source.
UI_UX_SPECIFICATION.md | Page inventory, user flows, forms, actions, empty/error states, responsive behavior.
TESTING_PLAN.md | Test strategy, test IDs, expected results, system and usability testing.
REQUIREMENTS_TRACEABILITY.md | Maps requirements to implementation, tests, and dissertation evidence.
DECISIONS.md | Architecture/design decision records and justifications.
README.md | Setup, run, test, migrate, seed, and deployment instructions.
CHANGELOG.md (optional) | Human-readable milestone changes.
[/TABLE]
