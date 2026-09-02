from app.extensions import db
from app.matching.service import (
    compute_application_match,
    recommend_opportunities_for_user,
    suggest_skills_for_text,
)
from app.models import FreelanceOpportunity, Skill, UserSkill


def _add_skill(user, name):
    skill = db.session.scalar(db.select(Skill).filter_by(name=name))
    if skill is None:
        skill = Skill(name=name)
        db.session.add(skill)
        db.session.flush()
    db.session.add(UserSkill(user=user, skill=skill, proficiency_level="Intermediate"))
    db.session.commit()
    return skill


def test_recommend_ranks_relevant_opportunity_above_irrelevant_one(app, user_factory):
    freelancer = user_factory(email="dev@example.com")
    freelancer.bio = "Experienced Python developer building web applications."
    _add_skill(freelancer, "Python")

    owner = user_factory(email="client@example.com", role_name="client")
    relevant = FreelanceOpportunity(
        client=owner,
        title="Python backend engineer",
        description="Build a Python API for our platform.",
    )
    unrelated = FreelanceOpportunity(
        client=owner,
        title="Logo design",
        description="Create a brand logo and identity guidelines.",
    )
    db.session.add_all([relevant, unrelated])
    db.session.commit()

    ranked = recommend_opportunities_for_user(freelancer, [relevant, unrelated], limit=2)

    assert ranked, "expected at least one recommendation"
    assert ranked[0][0].id == relevant.id


def test_recommend_returns_empty_for_blank_profile(app, user_factory):
    freelancer = user_factory(email="blank@example.com")
    owner = user_factory(email="client2@example.com", role_name="client")
    opportunity = FreelanceOpportunity(client=owner, title="Any work", description="Any work at all.")
    db.session.add(opportunity)
    db.session.commit()

    assert recommend_opportunities_for_user(freelancer, [opportunity]) == []
    assert recommend_opportunities_for_user(freelancer, []) == []


def test_suggest_skills_matches_whole_words_only(app):
    db.session.add_all([Skill(name="JavaScript"), Skill(name="Java")])
    db.session.commit()

    matches = suggest_skills_for_text("I write javascript for the frontend.")
    matched_names = {skill.name for skill in matches}

    assert "JavaScript" in matched_names
    assert "Java" not in matched_names


def test_suggest_skills_returns_empty_for_blank_text(app):
    Skill_row = Skill(name="SEO")
    db.session.add(Skill_row)
    db.session.commit()

    assert suggest_skills_for_text("") == []
    assert suggest_skills_for_text("   ") == []


def test_compute_application_match_scores_and_missing_skills(app, user_factory):
    applicant = user_factory(email="applicant@example.com")
    _add_skill(applicant, "Python")

    owner = user_factory(email="client3@example.com", role_name="client")
    opportunity = FreelanceOpportunity(
        client=owner,
        title="Python and SQL developer",
        description="Looking for someone skilled in Python and SQL.",
    )
    db.session.add_all([Skill(name="SQL"), opportunity])
    db.session.commit()

    result = compute_application_match(
        applicant, opportunity, cover_message="I have built several Python projects."
    )

    assert result["score"] > 0
    assert result["missing_skills"] == ["SQL"]


def test_precision_at_k_recommends_relevant_opportunities_first(app, user_factory):
    freelancer = user_factory(email="designer@example.com")
    freelancer.bio = "Graphic designer specializing in branding and logo design."
    _add_skill(freelancer, "Graphic Design")

    owner = user_factory(email="client4@example.com", role_name="client")
    relevant = [
        FreelanceOpportunity(client=owner, title="Brand logo design", description="Design a logo and brand identity."),
        FreelanceOpportunity(client=owner, title="Marketing graphics", description="Create graphic design assets for a campaign."),
    ]
    irrelevant = [
        FreelanceOpportunity(client=owner, title="Database migration", description="Migrate a SQL database to a new server."),
        FreelanceOpportunity(client=owner, title="Mobile app testing", description="Test a mobile application for bugs."),
    ]
    db.session.add_all(relevant + irrelevant)
    db.session.commit()

    relevant_ids = {item.id for item in relevant}
    ranked = recommend_opportunities_for_user(freelancer, relevant + irrelevant, limit=2)
    top_k_ids = {opportunity.id for opportunity, _ in ranked}

    precision_at_2 = len(top_k_ids & relevant_ids) / len(ranked) if ranked else 0
    assert precision_at_2 >= 0.5
