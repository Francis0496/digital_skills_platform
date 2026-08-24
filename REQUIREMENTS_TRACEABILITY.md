# REQUIREMENTS_TRACEABILITY.md

## Purpose
Map approved requirements to implementation modules, tests, and dissertation evidence.

| Requirement | Module | Expected Implementation | Test Prefix | Dissertation Evidence |
|---|---|---|---|---|
| FR01 | Authentication | `app/auth/routes.py:register`, `app/models:User` — Tested | AUTH-02, AUTH-03, AUTH-04 | Ch. 4 + Ch. 5 |
| FR02 | Authentication | `app/auth/routes.py:login/logout` — Tested | AUTH-05, AUTH-06, AUTH-07, AUTH-08 | Ch. 5 |
| FR03 | RBAC | `app/auth/decorators.py:roles_required` — Tested | ROLE-01, ROLE-02, ROLE-03 | Ch. 4 + Ch. 5 |
| FR04 | Profiles | `app/users/routes.py:profile/edit_profile`, ProfileForm and responsive templates — Tested | PROFILE-01 to PROFILE-08, MENTOR-01 to MENTOR-03 | Ch. 5 |
| FR05 | Skills | `Skill`, `UserSkill`, `/users/skills` add/remove workflows — Tested | SKILL-01 to SKILL-06 | Ch. 4 + Ch. 5 |
| FR06 | Courses | `app/admin/routes.py` category/course create and edit with publishing — Tested | COURSE-03 to COURSE-05 | Ch. 5 |
| FR07 | Courses | administrator lesson create/edit and per-course ordering — Tested | COURSE-04, COURSE-06 | Ch. 5 |
| FR08 | Courses | `/courses/` catalogue and published detail visibility — Tested | COURSE-01, COURSE-02 | Ch. 5 |
| FR09 | Courses | `Enrollment`, `/courses/<id>/enrol`, My Courses — Tested | ENROL-01 to ENROL-03 | Ch. 4 + Ch. 5 |
| FR10 | Courses | protected learning routes, LessonProgress and calculated progress — Tested | LEARNING-01 to LEARNING-05 | Ch. 5 |
| FR11 | Portfolio | `Portfolio`, own edit and public read-only showcase — Tested | PORTFOLIO-01 to PORTFOLIO-03, PORTFOLIO-05 | Ch. 5 |
| FR12 | Portfolio | owned project CRUD and safe image processing — Tested | PORTFOLIO-04, PORTFOLIO-06, PORTFOLIO-07 | Ch. 5 |
| FR13 | Opportunities | `FreelanceOpportunity` and owned create/edit/close workflows — Tested | JOB-01 to JOB-04, JOB-07 to JOB-09 | Ch. 5 |
| FR14 | Opportunities | active catalogue, details, keyword search and category filter — Tested | JOB-05, JOB-06 | Ch. 5 |
| FR15 | Applications | JobApplication and protected application submission — Tested | APP-01 to APP-04, APP-09 | Ch. 5 |
| FR16 | Applications | owned client review and controlled status updates — Tested | APP-05, APP-06, APP-08 | Ch. 5 |
| FR17 | Applications | private freelancer My Applications and details — Tested | APP-01, APP-07 | Ch. 5 |
| FR18 | Mentorship | public active mentor directory and details — Tested | MENTOR-01, MENTOR-02 | Ch. 5 |
| FR19 | Mentorship | freelancer request workflow with duplicate prevention — Tested | MENTOR-03, MENTOR-04, MENTOR-09 | Ch. 5 |
| FR20 | Mentorship | recipient-only accept/reject workflow — Tested | MENTOR-05 to MENTOR-08 | Ch. 5 |
| FR21 | Mentorship | active Mentorship records and role-specific views — Tested | MENTOR-05, MENTOR-10 | Ch. 4 + Ch. 5 |
| FR22 | Notifications | event service, centre, unread state and recipient-scoped read routes — Tested | NOTIFY-01 to NOTIFY-05 | Ch. 5 |
| FR23 | Administration | live platform-statistics dashboard — Tested | ADMIN-02 | Ch. 5 |
| FR24 | Administration | user search and activation/deactivation — Tested | ADMIN-01, ADMIN-03 | Ch. 5 |
| FR25 | Administration | skills plus existing category/course/lesson management — Tested | ADMIN-04, COURSE-03 to COURSE-06 | Ch. 5 |
| FR26 | Administration | opportunity, application, mentor and mentorship oversight — Tested | ADMIN-05, APP-10, JOB-04 | Ch. 5 |
| FR27 | Mentorship Workspace | participant-only active relationship workspace — Tested | WORKSPACE-01 to WORKSPACE-03 | Ch. 4 + Ch. 5 |
| FR28 | Mentorship Goals | participant creation, validation and secure completion — Tested | WORKSPACE-04 to WORKSPACE-06 | Ch. 5 |
| FR29 | Mentorship Progress | mentee-only progress with optional same-workspace goal — Tested | WORKSPACE-07, WORKSPACE-08 | Ch. 5 |
| FR30 | Mentor Feedback | assigned-mentor feedback with same-workspace associations — Tested | WORKSPACE-09, WORKSPACE-10 | Ch. 5 |
| FR31 | Mentorship Activity | timestamp-derived goal, progress, feedback and relationship history — Tested | WORKSPACE-01, WORKSPACE-11 | Ch. 4 + Ch. 5 |
| FR32 | Mentorship Notifications | participant-scoped goal, progress, feedback and completion notifications — Tested | WORKSPACE-04, WORKSPACE-06, WORKSPACE-07, WORKSPACE-09 | Ch. 5 |

| NFR-S01 | Security | production configuration, cookies, CSP and response headers in `config.py` and `app/__init__.py` - Verified | HARDEN-01 to HARDEN-03 | Ch. 5 + deployment evidence |
| NFR-D01 | Deployment | local Tailwind asset, `wsgi.py`, `Procfile`, `/health`, and `DEPLOYMENT.md` - Verified | HARDEN-04, HARDEN-05 | Ch. 5 + deployment evidence |

## Update Rule
Whenever a requirement is implemented:
1. Add the exact file/module/route.
2. Add the exact test IDs.
3. Add screenshot/evidence IDs once available.
4. Mark completion status.

## Status Convention
- Planned
- In Progress
- Implemented
- Tested
- Verified
