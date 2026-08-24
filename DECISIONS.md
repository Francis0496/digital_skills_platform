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

## ADR-011: No AI Matching in Prototype
**Decision:** Exclude AI-based job or mentor recommendations.

**Reason:** The core project can meet its objectives without adding an unnecessary feature that increases risk and scope.
