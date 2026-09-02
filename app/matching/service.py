import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.extensions import db
from app.models import Skill


def _user_profile_text(user):
    skill_names = " ".join(user_skill.skill.name for user_skill in user.skills)
    return f"{user.bio or ''} {skill_names}".strip()


def _opportunity_text(opportunity):
    return f"{opportunity.title} {opportunity.description}".strip()


def recommend_opportunities_for_user(user, opportunities, limit=3):
    """Rank `opportunities` against `user`'s bio + skill names.

    Fits one TfidfVectorizer per call over [user_text, *opportunity_texts].
    The dataset is small (prototype scale), so a fresh fit per request is
    cheap and needs no caching or persisted vectorizer.

    Returns a list of (opportunity, score) tuples sorted by score
    descending, score in [0, 1], positive-score-only, truncated to `limit`.
    """
    user_text = _user_profile_text(user)
    if not user_text or not opportunities:
        return []
    corpus = [user_text] + [_opportunity_text(o) for o in opportunities]
    try:
        matrix = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), min_df=1
        ).fit_transform(corpus)
    except ValueError:
        return []  # empty vocabulary (e.g. all-stopword text)
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    ranked = sorted(zip(opportunities, scores), key=lambda pair: pair[1], reverse=True)
    return [(opportunity, float(score)) for opportunity, score in ranked if score > 0][:limit]


_WORD_SPLIT = re.compile(r"[^a-z0-9]+")


def _normalize(text):
    return f" {_WORD_SPLIT.sub(' ', text.lower()).strip()} "


def suggest_skills_for_text(text, known_skills=None, limit=8):
    """Suggest Skill rows whose name is a whole-word/phrase match in `text`.

    Skill.name values are short controlled-vocabulary labels (e.g. "SEO",
    "Graphic Design"), not documents, so a TF-IDF/cosine-similarity
    comparison between a label and a paragraph would share almost no
    vocabulary by construction. Whole-word substring matching on
    normalized, whitespace-padded text is simpler, more precise, and
    easier to justify and evaluate for this kind of short-label matching.
    """
    if not text or not text.strip():
        return []
    haystack = _normalize(text)
    if known_skills is None:
        known_skills = db.session.scalars(db.select(Skill).order_by(Skill.name)).all()
    matches = [skill for skill in known_skills if _normalize(skill.name) in haystack]
    matches.sort(key=lambda skill: len(skill.name), reverse=True)
    return matches[:limit]


def compute_application_match(applicant, opportunity, cover_message=""):
    """Score how well `applicant` (bio + skills + cover letter) matches
    `opportunity` (title + description), and list opportunity-implied
    skills the applicant hasn't mentioned anywhere.

    Returns {"score": float 0-100 (1dp), "missing_skills": [name, ...]}.
    """
    applicant_text = f"{_user_profile_text(applicant)} {cover_message or ''}".strip()
    opportunity_text = _opportunity_text(opportunity)
    score = 0.0
    if applicant_text and opportunity_text:
        try:
            matrix = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), min_df=1
            ).fit_transform([applicant_text, opportunity_text])
            score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0]) * 100
        except ValueError:
            score = 0.0

    implied_skills = suggest_skills_for_text(opportunity_text)
    have_names = {user_skill.skill.name for user_skill in applicant.skills}
    mentioned_names = {skill.name for skill in suggest_skills_for_text(cover_message or "")}
    missing_skills = [
        skill.name
        for skill in implied_skills
        if skill.name not in have_names and skill.name not in mentioned_names
    ]

    return {"score": round(score, 1), "missing_skills": missing_skills}
