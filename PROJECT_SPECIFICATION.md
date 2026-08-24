# PROJECT_SPECIFICATION.md

## Project Title
**Development of a Digital Skills and Freelancing Platform for Youth in Sierra Leone: A Case Study of Youth in Freetown**

## Project Type
Project-based undergraduate dissertation with a fully functional web prototype.

## Vision
Provide a localised digital platform through which youth in Freetown can learn practical digital skills, build professional profiles and portfolios, access freelance opportunities, receive mentorship, and progress toward digital work.

## Problem Definition
Young people interested in digital work often depend on separate platforms for training, portfolios, mentorship, and freelance opportunities. International freelance marketplaces also assume users already have mature profiles, portfolios, experience, and knowledge of online work. The proposed system addresses this fragmented pathway by integrating digital learning and freelancing support in one web application.

## Aim
To design and develop a web-based Digital Skills and Freelancing Platform that supports digital skills development and facilitates access to freelancing opportunities for youth in Freetown, Sierra Leone.

## Objectives
1. Analyse and document the requirements for digital learning, portfolio development, freelancing, mentorship, and administration.
2. Design the architecture, database, interfaces, access control, and workflows.
3. Implement secure authentication and role-based access.
4. Implement learning, profiles, portfolios, opportunities, applications, mentorship, notifications, and administration.
5. Test the prototype against approved functional and non-functional requirements.
6. Deploy and document a working prototype.

## User Roles

### Freelancer/Learner
Can:
- Register and log in.
- Manage own profile.
- Add digital skills.
- Browse courses.
- Enrol in courses.
- Access lessons.
- Track progress.
- Create and manage a portfolio.
- Browse freelance opportunities.
- Apply to opportunities.
- Track applications.
- Browse mentors.
- Request mentorship.
- View notifications.

### Mentor
Can:
- Log in.
- Manage mentor profile.
- Specify expertise and availability.
- View mentorship requests addressed to them.
- Accept or reject requests.
- View active mentees.
- View notifications.

### Client/Opportunity Provider
Can:
- Register and log in.
- Manage client profile.
- Create and manage own opportunities.
- View applications to own opportunities.
- Review freelancer profiles and portfolios.
- Update application status.
- View notifications.

### Administrator
Can:
- Log in.
- View platform statistics.
- Manage users and account status.
- Manage courses, categories, lessons, and skills.
- Manage/monitor opportunities.
- Monitor applications.
- Manage mentors and mentorship records.
- Moderate platform content.

## In-Scope Features
- Registration and authentication.
- Role-based access control.
- Account activation/deactivation.
- User profiles.
- Digital skills.
- Course categories, courses, and lessons.
- Enrolment and learning progress.
- Portfolio and portfolio projects.
- Freelance opportunity marketplace.
- Search/filter for opportunities.
- Applications and application statuses.
- Mentor directory.
- Mentorship requests and active mentorships.
- In-app notifications.
- Administrator dashboard and management tools.
- Responsive UI.
- System testing and deployment.

## Out-of-Scope Features
- Native Android or iOS apps.
- Direct Upwork/Fiverr integration.
- Online payment processing.
- Mobile money integration.
- Escrow.
- Real-time video conferencing.
- AI job matching.
- Enterprise microservices.
- Long-term employment impact measurement.

## Functional Requirements

### FR01 Registration
The system shall allow eligible users to register using a unique email address.

### FR02 Authentication
The system shall allow active users to log in and log out securely.

### FR03 Role-Based Access
The system shall restrict protected actions according to user role.

### FR04 Profile Management
Users shall create and update role-appropriate profile information.

### FR05 Skills Management
Freelancers shall manage digital skills associated with their profiles.

### FR06 Course Management
Administrators shall create, edit, publish/unpublish, and manage courses and categories.

### FR07 Lesson Management
Administrators shall create and order lessons within courses.

### FR08 Course Browsing
Users shall browse published courses.

### FR09 Course Enrolment
Learners shall enrol once in available courses.

### FR10 Learning Progress
Learners shall record lesson completion and view course progress.

### FR11 Portfolio Management
Freelancers shall create and manage a professional portfolio.

### FR12 Portfolio Projects
Freelancers shall add, edit, and remove their own portfolio projects.

### FR13 Opportunity Management
Clients shall create, edit, close, and manage their own opportunities.

### FR14 Opportunity Discovery
Freelancers shall browse, search, and filter active opportunities.

### FR15 Applications
Freelancers shall submit one application per active opportunity.

### FR16 Application Review
Clients shall review applications to their own opportunities and update status.

### FR17 Application Tracking
Freelancers shall track submitted applications.

### FR18 Mentor Directory
Freelancers shall browse mentor profiles.

### FR19 Mentorship Requests
Freelancers shall submit mentorship requests.

### FR20 Mentorship Response
Mentors shall accept or reject pending requests.

### FR21 Mentorship Records
The system shall maintain active mentorship relationships.

### FR22 Notifications
The system shall create in-app notifications for important events.

### FR27 Mentorship Workspace
Mentors and freelancers shall access a private workspace for their own active mentorship relationship.

### FR28 Mentorship Goals
Both participants shall create development goals and securely mark them completed.

### FR29 Mentorship Progress
The freelancer, acting as mentee, shall post structured progress updates with an optional relationship goal.

### FR30 Mentor Feedback
The assigned mentor shall provide structured feedback associated with the relationship, a goal, or a progress update.

### FR31 Mentorship Activity
The workspace shall present a derived history of relationship, goal, progress, and feedback events.

### FR32 Mentorship Workspace Notifications
The system shall notify only the other mentorship participant about goals, completion, progress, and feedback.

### FR23 Admin Dashboard
Administrators shall view core platform statistics.

### FR24 User Administration
Administrators shall search, inspect, activate, deactivate, and manage users.

### FR25 Content Administration
Administrators shall manage skills, courses, lessons, and approved platform content.

### FR26 Platform Oversight
Administrators shall monitor opportunities, applications, mentors, and mentorship records.

## Non-Functional Requirements
- **Usability:** consistent and understandable UI.
- **Responsiveness:** desktop, laptop, tablet, and smartphone support.
- **Security:** password hashing, CSRF, authentication, authorization, ownership checks.
- **Data integrity:** unique constraints, foreign keys, validation.
- **Performance:** acceptable prototype response times.
- **Reliability:** consistent behavior under normal use.
- **Maintainability:** application factory, Blueprints, modular code.
- **Portability:** configuration separated from environment-specific values.
- **Compatibility:** modern Chrome, Edge, and Firefox.
- **Testability:** repeatable automated tests for core rules.

## Business Rules
1. Every account uses a unique email.
2. Passwords are never stored as plain text.
3. Every user has one primary role.
4. Protected actions require authentication and server-side authorization.
5. Deactivated users cannot use protected functionality.
6. A learner cannot enrol in the same course twice.
7. Lesson progress can only be recorded for the current learner's enrolment.
8. Users may only modify owned or authorized records.
9. Only clients and administrators may create opportunities.
10. Only freelancers may apply to opportunities.
11. Duplicate applications are not allowed.
12. Closed or expired opportunities cannot accept applications.
13. Application statuses: Pending, Under Review, Accepted, Rejected.
14. Only freelancers may initiate mentorship requests.
15. Mentorship becomes active only after mentor acceptance.
16. Administrators may deactivate users and moderate managed records.
17. Administrator access is never granted via public registration.
18. Referential integrity must be preserved.
19. Mentorship workspace content is available only to participants in an active relationship.
20. Only the relationship's freelancer may create progress updates.
21. Only the relationship's assigned mentor may create mentor feedback.
22. Child records may only reference goals or progress updates from the same mentorship.

## SDLC
Use an iterative SDLC:
Planning → Requirements Analysis → System Design → Development → Testing → Deployment → Evaluation/Maintenance

## Approved Stack
Python, Flask, Jinja2, HTML5, Tailwind CSS, JavaScript, Flask-SQLAlchemy, SQLite, Flask-Login, Flask-WTF, Werkzeug, Flask-Migrate, pytest, Git/GitHub.

## Prototype Completion Criteria
The project is complete when:
- All approved core modules work.
- Role permissions are enforced.
- Automated test suite passes.
- Manual system tests are completed.
- Responsive behavior is verified.
- Deployment works.
- User manual and dissertation evidence are prepared.
