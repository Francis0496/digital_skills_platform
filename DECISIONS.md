# DECISIONS.md

# Architecture Decision Records

## ADR-001: Project-Based Dissertation
**Decision:** The dissertation is centred on a working software artefact rather than a survey-heavy research project.

**Reason:** The Faculty format expects problem definition, methodology, analysis/design, results, system testing, and evaluation of an implemented system.

## ADR-002: Iterative SDLC
**Decision:** Use an iterative SDLC while retaining formal SDLC phases.

**Reason:** It supports controlled module-by-module implementation, testing, and refinement.

## ADR-003: Flask
**Decision:** Use Flask as backend framework.

**Reason:** Lightweight, suitable for the prototype, easy to structure with Blueprints, and appropriate for Python-based development.

## ADR-004: SQLite
**Decision:** Use SQLite for the prototype database.

**Reason:** Low administration, portable, relational, and sufficient for prototype-scale use.

**Production Note:** A larger deployment should consider PostgreSQL.

## ADR-005: SQLAlchemy
**Decision:** Use Flask-SQLAlchemy / SQLAlchemy.

**Reason:** Clear relational modelling, safer data access, easier migrations and future database portability.

## ADR-006: Flask-Login
**Decision:** Use Flask-Login for session authentication.

**Reason:** The application is server-rendered with Flask/Jinja2, so session authentication is simpler and more suitable than JWT.

## ADR-007: Tailwind CSS
**Decision:** Use Tailwind CSS for UI styling.

**Reason:** Rapid responsive design and consistent UI.

## ADR-008: Modular Monolith
**Decision:** Use a modular monolith with Blueprints.

**Reason:** Maintains separation of concerns without the complexity of microservices.

## ADR-009: In-App Notifications
**Decision:** Use database-backed in-app notifications for the prototype.

**Reason:** Meets the requirement without adding email/SMS infrastructure.

## ADR-010: No Payment Integration
**Decision:** Exclude online payment and mobile-money processing.

**Reason:** Payment introduces regulatory, security, and implementation complexity beyond the approved undergraduate prototype scope.

## ADR-011: Scoped Offline TF-IDF Matching (Revised)
**Decision:** Add one small, self-contained AI/NLP module (`app/matching/service.py`)
covering exactly three features: (1) TF-IDF + cosine-similarity ranking of
opportunities for a freelancer's "Recommended for you" list, (2) keyword-based
Skill-tag suggestions from bio/portfolio-project free text, and (3) a
cover-letter/opportunity match score with missing-skill feedback on the
application form. No external LLM API is used; scikit-learn's TfidfVectorizer
runs fully offline against data already in the platform's own database.

**Reason:** The original ADR-011 excluded AI matching to control scope. A
single, small, demoable, and rigorously evaluable NLP module (measured via
precision@k and skill-overlap tests, see `tests/test_matching.py`) is a
defensible addition for the dissertation's analysis/evaluation chapters
without expanding the system's surface area: no new blueprint (beyond a
package marker), no new database tables or migrations, and no third-party
network dependency. A skill-gap course recommender was considered and
explicitly deferred — it would require a new skills-per-course schema and is
out of scope for this addition.

**Note:** This directly reverses an explicit exclusion in
`Digital_Skills_Freelancing_Platform_Master_Development_Specification.docx`
§3.2 ("AI-based job matching or automated recommendation engines"). See
`SCOPE_AMENDMENTS.md` (Amendment 001) for the full justification and
project-owner approval record required by `AGENTS.md`.
