# CHANGELOG.md

All significant project changes should be recorded by increment.

## Unreleased

### Administrator Responsive Workspace Correction

- Refined Learning Content so category/course panels remain stacked at compact desktop widths and use a balanced split only on wide screens.
- Stabilized Category Edit and Course Manage actions with readable non-shrinking action groups.
- Corrected skill-management record actions so Edit remains content-sized and readable without shrinking.
- Corrected the wide-screen user-search row so its input flexes while Search and Clear remain readable, content-sized controls.
- Routed Administrator dashboard access directly to the implemented operational overview.
- Removed obsolete authentication, next-step, release, and Increment 9 interface wording.
- Reworked the authenticated top bar to prevent Dashboard and Logout labels from wrapping or competing with mobile controls.
- Kept mobile logout inside the existing CSRF-protected navigation drawer and made the dashboard menu trigger compact.
- Updated the Administrator welcome content to reflect the completed management workspace.

### Responsive Dashboard Card Correction

- Corrected learner summary-card breakpoints so cards remain readable beside the authenticated sidebar at compact desktop widths.
- Constrained shared UI icons and icon tiles to prevent stretching, clipping, and text-driven overflow across display sizes.
- Standardized badge sizing and wrapping so status labels remain content-sized on wide screens and safe on narrow screens.
- Hardened shared media, forms, buttons, headings, authenticated navigation, notifications, and content containers against viewport overflow.
- Advanced the static-asset version so browsers load the corrected responsive styles immediately.

### Batch 4: Administrator UI/UX Refinement
Status: Completed

Improved:
- Rebuilt the Administrator dashboard around existing user, role, course, opportunity, application, and mentorship counts.
- Added concise recent-user and quick-action sections using existing administrative routes.
- Standardized Administrator navigation using the shared responsive authenticated sidebar and icon system.
- Refined user management with semantic desktop tables, responsive mobile cards, identity cells, role/status badges, and secure account-status controls.
- Improved learning-content management with concise category, course, publication, difficulty, and lesson information.
- Refined skill and mentorship oversight presentation with consistent records, statuses, and empty states.
- Added responsive administrative layouts and focused UI regression coverage.

Scope:
- No administrative capability, model, migration, authentication, authorization, ownership, business rule, or deployment behavior changed.

### Batch 3: Mentor and Client UI/UX Refinement
Status: Completed

Improved:
- Added a mentor command-centre dashboard using live request, mentee, profile, and notification data.
- Added responsive mentor navigation with active states, accessible mobile behavior, and secure logout.
- Refined received-request review, status presentation, response controls, and empty states.
- Improved active-mentee cards with learner location, skills, and relationship start dates.
- Standardized mentor status badges, profile prompts, responsive cards, and page hierarchy.
- Added a client command-centre dashboard using live opportunity, application, review, and notification data.
- Standardized client navigation using the shared responsive authenticated sidebar.
- Refined opportunity creation and editing with grouped, readable form sections.
- Improved opportunity lifecycle management, application counts, and secure management actions.
- Rebuilt applicant lists and application detail views around proposal, profile, portfolio, and status-review information.
- Added responsive client cards, review layouts, status badges, and useful empty states.

Scope:
- No mentorship or application rules, models, migrations, authentication, authorization, ownership, or notification-generation logic changed.

### Batch 2: Freelancer/Learner UI/UX Refinement
Status: Completed

Improved:
- Rebuilt the learner dashboard around live course, application, portfolio, mentorship, opportunity, and notification data.
- Standardized authenticated learner navigation with a persistent desktop sidebar and accessible mobile drawer.
- Refined profile and skills presentation while preserving existing fields and secure upload behavior.
- Improved course cards, progress presentation, learning navigation, and mobile lesson usability.
- Strengthened portfolio project presentation and owner-focused empty-state actions.
- Refined opportunity, application, mentor discovery, mentorship request, and notification interfaces.
- Added responsive learner layouts, consistent iconography, compact cards, and accessible native progress indicators.

Scope:
- No model, migration, schema, business-rule, authentication, authorization, or deployment changes were introduced.

### Batch 1: Branding and Global UI/UX Refinement
Status: Completed

Improved:
- Integrated the approved Digital Skills Platform logo, favicon set, and brand tokens.
- Refined the shared public navbar, active states, accessible mobile menu, flash messages, and footer.
- Rebuilt the homepage around real courses, active opportunities, mentorship, and working platform pathways.
- Added the specified public About page and removed obsolete homepage increment placeholders.
- Refined login and registration with responsive branded layouts, clearer hierarchy, password guidance, and accessible validation states.
- Standardized public buttons, cards, links, forms, icons, focus states, and responsive spacing.

Homepage correction:
- Made desktop navigation and mobile-menu switching resilient at the 1024px breakpoint.
- Added versioned static asset URLs to prevent stale Tailwind and component CSS after releases.
- Reduced the hero to a focused content-driven layout with readable copy and content-sized actions.
- Removed the decorative hero checkmark row and oversized visual-card composition.
- Made pathway, course, opportunity, mentorship, final CTA, and footer layouts compact and breakpoint-safe.
- Removed the custom container's dependency on Tailwind preflight for border-box sizing, eliminating the identified page-overflow risk.

Scope:
- No business workflow, authorization rule, model, migration, or database schema was changed.

### Increment 10: Hardening and Deployment
Status: Completed

Added:
- Explicit production configuration with strong-secret validation and secure cookies.
- CSP, HSTS, clickjacking, MIME-sniffing, referrer, and permissions response headers.
- Database-aware `/health` readiness endpoint and Waitress WSGI deployment entrypoint.
- Reproducible, minified local Tailwind build with pinned Node dependencies.
- CSP-safe confirmation handlers, accessible user search labelling, and deployment guidance.

Testing:
- Production startup, cookies, headers, health, local assets, and inline-handler regression tests pass.
- Full suite: 129 passed; Python dependency check and npm vulnerability audit pass.

### Increment 9: Administration and Notifications
Status: Completed

Added:
- Database-backed notifications with unread badges and recipient-scoped read controls.
- Notifications for enrolment, applications, application status, and mentorship events.
- Administrator statistics dashboard, user search/activation, and skill management.
- Consolidated opportunity, application, learning, and mentorship oversight.
- Responsive management views, notification migration, and privacy/authorization tests.

Testing:
- Recipient privacy, read state, event delivery, administrator access, user state, skills, statistics, and oversight tests pass.

### Increment 8: Mentorship
Status: Completed

Added:
- Public active-mentor directory and professional mentor details.
- Freelancer mentorship requests with duplicate pending/active prevention.
- Recipient-only mentor acceptance and rejection.
- Active mentorship relationship records, learner tracking, and mentor mentee views.
- Responsive request, directory, profile, and mentee interfaces.
- Mentorship migration and lifecycle/privacy tests.

Testing:
- Directory visibility, role access, duplicates, recipient ownership, response lifecycle, and mentee privacy tests pass.

### Increment 7: Applications
Status: Completed

Added:
- JobApplication model with one application per freelancer and opportunity.
- Freelancer application submission and status tracking.
- Closed/expired opportunity and duplicate-application protection.
- Owned client applicant review with profile, skills, and portfolio context.
- Pending, Under Review, Accepted, and Rejected status controls.
- Administrator application oversight, responsive views, migration, and access tests.

Testing:
- Submission, lifecycle, duplicate, role, privacy, ownership, status-tampering, and oversight tests pass.

### Increment 6: Freelance Marketplace
Status: Completed

Added:
- Client-owned freelance opportunities with active, closed, and expired lifecycle states.
- Client and administrator create/edit controls with ownership enforcement.
- Public active-opportunity catalogue, keyword search, category filtering, and details.
- Client My Opportunities and administrator oversight interfaces.
- POST-only closing, deadline/budget validation, responsive marketplace views, migration, and security tests.

Testing:
- Role, ownership, lifecycle, visibility, filtering, validation, and direct-route tests pass.

### Increment 5: Portfolio
Status: Completed

Added:
- One-to-one freelancer portfolios and owned portfolio projects.
- Portfolio introduction and project create, edit, and delete workflows.
- Public read-only portfolio showcases with owner-only controls.
- Safe randomized WebP project-image processing and replacement cleanup.
- Responsive project cards, empty states, validation, and ownership tests.
- Portfolio schema migration.

Testing:
- Portfolio uniqueness, role authorization, ownership, image validation, public visibility, and CRUD tests pass.

### Increment 4: Digital Learning
Status: Completed

Added:
- CourseCategory, Course, Lesson, Enrollment, and LessonProgress models.
- Administrator category, course, publishing, and ordered-lesson management.
- Published public course catalogue with category and difficulty filters.
- Course details and lesson overview.
- Freelancer enrolment with duplicate prevention.
- My Courses, protected learning screen, lesson navigation, and completion tracking.
- Calculated textual and visual progress with completion status.
- Digital-learning migration and authorization/regression tests.

Changed:
- Public and freelancer navigation now links to live learning workflows.
- Home-page learning actions now open the real course catalogue.
- Requirements traceability now records tested implementations for FR06-FR10.

Testing:
- Publishing visibility, administrator access, enrolment, lesson ownership, constraints, and progress tests pass.

### Increment 3: Profiles and Skills
Status: Completed

Added:
- Skill, UserSkill, and MentorProfile models with approved relationships and uniqueness constraints.
- Own-profile view and edit workflows for all authenticated roles.
- Safe profile-image validation, resizing, randomized naming, WebP re-encoding, private storage, and replacement cleanup.
- Freelancer skill management with Beginner, Intermediate, and Advanced proficiency levels.
- Mentor professional-title, expertise, experience, and availability editing.
- Responsive profile, skills, and mentor-profile interfaces.
- Increment 3 schema migration and comprehensive profile/skill tests.

Changed:
- Role navigation now links to the profile features available in Increment 3.
- Dashboard next steps now point users to live profile workflows.
- Requirements traceability now records tested implementations for FR04 and FR05.

Testing:
- Profile validation, image security, ownership, database constraints, skill access, and mentor access tests pass.

### Increment 2: Authentication and Role-Based Access Control
Status: Completed

Added:
- Role and User models with approved fields, relationships, and uniqueness rules.
- Werkzeug password hashing and Flask-Login user loading.
- Public registration, login, and POST-only logout flows.
- Inactive-account enforcement and safe post-login redirects.
- Reusable server-side role authorization decorator.
- Responsive authentication forms and templates.
- Initial Role/User migration and idempotent `seed-roles` command.
- Authentication and RBAC regression tests.
- Responsive public navigation, authenticated layout, and role dashboard shells.
- Reusable design-system styles for buttons, forms, alerts, cards, badges, sidebars, and empty states.

Changed:
- Navigation now reflects anonymous and authenticated session state.
- Foundation and authentication pages now use the approved indigo, teal, and semantic colour system.
- Unimplemented role navigation is presented as disabled text instead of fake links.
- Requirements traceability and setup documentation now cover FR01-FR03.

Testing:
- Foundation, model, authentication, account-state, redirect, RBAC, and role-layout tests pass.

### Increment 1: Project Foundation
Status: Completed

Added:
- Flask application factory and environment-based configuration.
- SQLAlchemy, Flask-Migrate, Flask-Login, and CSRF extension setup.
- Blueprint skeletons for all planned application areas.
- Responsive Tailwind-based home page and shared Jinja layout.
- Custom 403, 404, and 500 error pages.
- Isolated pytest configuration and foundation smoke tests.
- Environment, ignore, dependency, and static asset files.

Changed:
- Expanded README with verified setup, run, test, migration, and styling guidance.

Testing:
- Foundation test suite and application/migration smoke checks completed.

Notes:
- Business models and functionality remain deferred to later increments.
- Tailwind uses the browser CDN for this foundation and should be compiled for production.

## Format for Future Entries

### Increment N: Name
Status: Completed / In Progress

Added:
- ...

Changed:
- ...

Fixed:
- ...

Testing:
- ...

Notes:
- ...
