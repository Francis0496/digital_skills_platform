# Digital Skills and Freelancing Platform

## Project
Development of a Digital Skills and Freelancing Platform for Youth in Sierra Leone: A Case Study of Youth in Freetown.

## Status
All 10 approved increments are complete, including production hardening and deployment preparation.

## Approved Stack
- Python
- Flask
- Jinja2
- Tailwind CSS
- JavaScript
- SQLAlchemy / Flask-SQLAlchemy
- SQLite
- Flask-Login
- Flask-WTF
- Flask-Migrate
- pytest

## Documentation
Read these before implementation:
1. `AGENTS.md`
2. `PROJECT_SPECIFICATION.md`
3. `DATABASE_DESIGN.md`
4. `UI_UX_SPECIFICATION.md`
5. `PLATFORM_DESIGN_SYSTEM.md`
6. `TESTING_PLAN.md`
7. `REQUIREMENTS_TRACEABILITY.md`
8. `DECISIONS.md`
9. `CURRENT_INCREMENT.md`

## Development Process
The project is built one verified increment at a time.

Current sequence:
1. Foundation
2. Authentication and RBAC
3. Profiles and Skills
4. Digital Learning
5. Portfolio
6. Freelance Marketplace
7. Applications
8. Mentorship
9. Administration and Notifications
10. Hardening and Deployment

## Prerequisites

- Python 3.10 or newer
- pip
- Git
- Node.js and npm when rebuilding frontend assets

## Environment Setup

Create a virtual environment:

```text
python -m venv .venv
```

Activate it on Windows PowerShell:

```text
.venv\Scripts\Activate.ps1
```

Activate it on macOS or Linux:

```text
source .venv/bin/activate
```

Install dependencies:

```text
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace the example secret with a long,
random value. The default SQLite database is created under `instance/`.

## Run the Application

```text
python run.py
```

Open `http://127.0.0.1:5000/`. Debug mode is enabled only by the development
configuration and must not be used in production.

## Run Tests

```text
python -m pytest
```

Tests use an isolated in-memory SQLite database and do not modify the
development database.

## Database Migrations

Migration support is configured. Initialize the migrations directory only once
in a repository that does not already contain it:

```text
flask --app run.py db init
```

After adding or changing models in a later increment, run:

```text
flask --app run.py db migrate -m "Describe the schema change"
flask --app run.py db upgrade
```

Apply the current Role/User migration and seed the four approved roles:

```text
flask --app run.py db upgrade
flask --app run.py seed-roles
```

The seed command is idempotent and safe to run more than once. Public
registration supports freelancer, mentor, and client accounts; administrator
accounts are never created through public registration.

Create an administrator from a trusted local terminal. The password is hidden,
confirmed, and never placed in shell history:

```text
flask --app run.py create-admin --full-name "Administrator Name" --email admin@example.com
```

## Tailwind CSS

Tailwind is compiled locally; the application has no browser-CDN dependency.
Install the pinned build dependencies and rebuild after changing template utility
classes:

```text
npm install
npm run build:css
```

The minified output at `app/static/css/tailwind.css` is committed for deployment.
See `DEPLOYMENT.md` for production configuration, migration, health-check, and
Waitress startup instructions.

## Project Structure

- `app/__init__.py`: application factory, registration, error handling, logging
- `app/extensions.py`: unbound Flask extensions
- `app/main/`: public foundation routes
- `app/auth/`: forms, registration/login/logout routes, and role authorization
- `app/models/`: Role and User persistence plus approved role seeding
- `app/users/`: own-profile, profile-image, freelancer-skill, and mentor-profile workflows
- `app/courses/`: published catalogue, enrolment, learning, and lesson progress
- `app/admin/`: administrator learning-content management
- `app/portfolio/`: freelancer portfolio showcase and owned project management
- `app/opportunities/`: public opportunity discovery and owned client management
- `app/applications/`: freelancer submissions, client review, status tracking, and oversight
- `app/mentorship/`: mentor discovery, requests, responses, and active relationships
- `app/notifications/`: event service and private read/unread notification centre
- `app/admin/`: statistics, user status, skills, learning, and platform oversight
- `app/templates/layouts/`: responsive authenticated dashboard shell
- `app/static/css/app.css`: reusable platform design-system patterns
- `app/static/css/tailwind.css`: compiled, minified Tailwind release asset
- Other `app/` packages: registered Blueprint skeletons for later increments
- `app/templates/`: shared layout, home page, and error pages
- `tests/`: isolated pytest fixtures and foundation smoke tests

## Profile Images

Profile images accept JPG, PNG, and WebP uploads within the 3 MB request limit.
The application verifies image content, corrects orientation, limits dimensions
to 800 by 800 pixels, and writes a randomized WebP file under the private
instance directory. Original filenames are not retained. Pillow is included
solely for this security and low-bandwidth image-processing workflow.

## Core Rule
Do not build the whole system in one pass. Complete and test each increment before proceeding to the next.
