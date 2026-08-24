# AGENTS.md

## Purpose
This file defines the mandatory engineering rules Codex must follow when working on the Digital Skills and Freelancing Platform.

## Authoritative Sources
When making changes, use the following files as the source of truth, in this order:
1. `AGENTS.md`
2. `PROJECT_SPECIFICATION.md`
3. `DATABASE_DESIGN.md`
4. `UI_UX_SPECIFICATION.md`
5. `PLATFORM_DESIGN_SYSTEM.md`
6. `TESTING_PLAN.md`
7. `REQUIREMENTS_TRACEABILITY.md`
8. `DECISIONS.md`
9. `CURRENT_INCREMENT.md`

Do not silently override these documents.

## Approved Technology Stack
- Python
- Flask
- Jinja2
- HTML5
- Tailwind CSS
- JavaScript
- Flask-SQLAlchemy / SQLAlchemy
- SQLite
- Flask-Login
- Flask-WTF / WTForms
- Werkzeug password hashing
- Flask-Migrate / Alembic
- pytest
- Git and GitHub

Do not replace the approved stack without explicit approval.

## Architecture Rules
- Use the Flask application factory pattern.
- Use Flask Blueprints.
- Keep the application as a modular monolith.
- Do not place the entire application in a single `app.py`.
- Separate models, routes, templates, forms, and reusable helpers where appropriate.
- Prefer clear, dissertation-friendly code over unnecessary abstraction.
- Do not introduce microservices, Kubernetes, Docker orchestration, or unrelated infrastructure.

## Database Rules
- Use SQLAlchemy models rather than raw SQL for normal application logic.
- Use Flask-Migrate/Alembic once migrations are established.
- Every schema change must include a migration.
- Preserve foreign-key integrity.
- Add unique constraints where business rules require uniqueness.
- Do not silently rename fields already used elsewhere.
- Avoid destructive data migrations unless explicitly approved.

## Authentication and Security
- Use Flask-Login for session authentication.
- Hash passwords with Werkzeug helpers.
- Never store passwords in plain text.
- Never commit secrets.
- Use environment variables for deployment secrets and configuration.
- Use Flask-WTF CSRF protection for state-changing HTML forms.
- Enforce authorization server-side.
- Never rely on hidden fields, URL parameters, or front-end controls for authorization.
- Validate ownership for user-owned records.
- Public registration must never create administrator accounts.
- Use safe filenames and an allowlist for uploaded file types.
- Disable debug mode in production.

## Development Rules
Before changing a module:
1. Inspect the relevant models, routes, templates, migrations, and tests.
2. Identify what already exists.
3. Make the smallest coherent change needed for the approved increment.
4. Preserve existing working functionality.
5. Do not invent features outside the project specification.
6. Do not refactor unrelated modules without approval.

## Testing Rules
- Run relevant tests before and after meaningful changes.
- Add tests for new business rules and access-control rules.
- Test happy paths, invalid input, and unauthorized access.
- Run the full suite before declaring an increment complete.
- Do not claim completion while tests are failing.
- If a test is intentionally deferred, document why.

## Definition of Done
A feature is complete only when:
- The requirement is implemented.
- Validation is implemented.
- Authentication and authorization are correct.
- Database changes are migrated.
- Important failure paths are handled.
- Tests are added or updated.
- Existing tests still pass.
- UI feedback is clear.
- Documentation and traceability are updated.
- No unrelated working functionality has been removed.

## Change Reporting
At the end of each increment, report:
1. What was implemented.
2. Files created or changed.
3. Database migrations added.
4. Tests created or updated.
5. Commands/tests executed and their results.
6. Acceptance criteria status.
7. Known limitations or unresolved decisions.

## Approval Required Before
- Changing the approved stack.
- Changing the project scope.
- Adding paid/external infrastructure.
- Introducing a new architectural pattern.
- Performing a large refactor.
- Removing an approved feature.
