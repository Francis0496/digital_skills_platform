# SCOPE_AMENDMENTS.md

Record of deviations from `Digital_Skills_Freelancing_Platform_Master_Development_Specification.docx`,
made under the explicit project-owner approval clause in that document's
Section 1 ("Purpose and Authority"): *"Where this specification conflicts
with an ad hoc coding suggestion, this specification takes precedence
unless the project owner explicitly approves a change."* Cross-referenced
from `DECISIONS.md` ADR-011.

## Amendment 001: Scoped Offline AI/NLP Matching Module

**Date:** 2026-08-29

**Original constraint:** Section 3.2, "Out of Scope for Initial Prototype,"
lists *"AI-based job matching or automated recommendation engines."*
`AGENTS.md` separately requires approval before "Changing the project
scope" and instructs "Do not invent features outside the project
specification."

**What was added:** A small, self-contained module (`app/matching/service.py`)
providing three features, all built on offline `scikit-learn` TF-IDF +
cosine similarity and whole-word keyword matching against data already in
the platform's own database — no external AI/LLM API, no new database
tables:
1. Opportunity recommendations for freelancers ("Recommended for you" on
   the dashboard).
2. Skill-tag suggestions from bio/portfolio-project free text.
3. Cover-letter/opportunity match scoring with missing-skill feedback on
   the application form.

**Why the deviation was approved:** The original exclusion was written to
control scope/risk for an undergraduate prototype. The project owner
reviewed the conflict directly against this specification and `AGENTS.md`
and approved a narrowly scoped addition — not a general "AI matching
engine" — on the basis that:
- It reuses existing schema and data only; no new tables, columns, or
  migrations (`app/models/__init__.py` unchanged).
- It is offline and dependency-light (`scikit-learn` added to
  `requirements.txt`; no network calls, no API keys, no availability risk
  during an offline demo or viva).
- It is rigorously testable and gives citable evaluation numbers
  (`tests/test_matching.py`: precision@k and skill-overlap assertions),
  which strengthens rather than weakens the dissertation's Results/
  Evaluation chapters (Master Specification §29 chapter table, Chapters
  Five and Six).
- A related idea — a skill-gap **course** recommender — was explicitly
  considered and **not** implemented, because it would require a new
  skills-per-course schema, which was judged out of proportion to the
  remaining time before submission. It is documented only as future work.

**What did not change:** All other Out of Scope items in Section 3.2
(native apps, payment processing, real-time video, microservices,
third-party marketplace integration, long-term outcome tracking) remain
excluded. The approved technology stack in `AGENTS.md` is unchanged except
for the addition of `scikit-learn`, which is a Python library used
identically to the existing SQLAlchemy/Flask stack (no new service,
infrastructure, or paid dependency).

**Superseded/updated documents:**
- `DECISIONS.md` ADR-011, revised from "No AI Matching in Prototype" to
  "Scoped Offline TF-IDF Matching (Revised)."
- `requirements.txt` — added `scikit-learn==1.9.0`.

**Suggested dissertation treatment:** Cite this file directly in Chapter
Two (Problem Definition and Scope) or Chapter Six (Recommendations) as
evidence of a controlled, justified, and tested scope change, rather than
silently presenting the feature as if it were in the original approved
specification.
