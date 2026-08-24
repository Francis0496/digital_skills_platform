from datetime import date
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from app.auth.decorators import roles_required
from app.extensions import db
from app.models import FreelanceOpportunity
from . import bp
from .forms import ActionForm, OpportunityForm

@bp.get("/")
def catalogue():
    statement = db.select(FreelanceOpportunity).where(
        FreelanceOpportunity.status == "active",
        db.or_(FreelanceOpportunity.deadline.is_(None), FreelanceOpportunity.deadline >= date.today()),
    )
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    if query:
        term = f"%{query}%"
        statement = statement.where(db.or_(FreelanceOpportunity.title.ilike(term), FreelanceOpportunity.description.ilike(term)))
    if category:
        statement = statement.where(FreelanceOpportunity.category == category)
    opportunities = db.session.scalars(statement.order_by(FreelanceOpportunity.created_at.desc())).all()
    categories = db.session.scalars(db.select(FreelanceOpportunity.category).where(FreelanceOpportunity.category.is_not(None)).distinct().order_by(FreelanceOpportunity.category)).all()
    return render_template("opportunities/catalogue.html", opportunities=opportunities, categories=categories, query=query, selected_category=category)

@bp.get("/<int:opportunity_id>")
def detail(opportunity_id):
    opportunity = db.get_or_404(FreelanceOpportunity, opportunity_id)
    return render_template("opportunities/detail.html", opportunity=opportunity, action_form=ActionForm())

@bp.get("/mine")
@roles_required("client")
def mine():
    opportunities = db.session.scalars(db.select(FreelanceOpportunity).where(FreelanceOpportunity.client_id == current_user.id).order_by(FreelanceOpportunity.created_at.desc())).all()
    return render_template("opportunities/mine.html", opportunities=opportunities, action_form=ActionForm())

@bp.get("/admin/all")
@roles_required("administrator")
def oversight():
    opportunities = db.session.scalars(db.select(FreelanceOpportunity).order_by(FreelanceOpportunity.created_at.desc())).all()
    return render_template("opportunities/mine.html", opportunities=opportunities, action_form=ActionForm(), oversight=True)

@bp.route("/new", methods=["GET", "POST"])
@roles_required("client", "administrator")
def create():
    form = OpportunityForm()
    if form.validate_on_submit():
        opportunity = FreelanceOpportunity(client=current_user, status="active")
        _apply_form(opportunity, form); db.session.add(opportunity); db.session.commit()
        flash("Opportunity created.", "success")
        return redirect(url_for("opportunities.detail", opportunity_id=opportunity.id))
    return render_template("opportunities/form.html", form=form, opportunity=None)

@bp.route("/<int:opportunity_id>/edit", methods=["GET", "POST"])
@roles_required("client", "administrator")
def edit(opportunity_id):
    opportunity = db.get_or_404(FreelanceOpportunity, opportunity_id); _ensure_manager(opportunity)
    form = OpportunityForm(obj=opportunity)
    if form.validate_on_submit():
        _apply_form(opportunity, form); db.session.commit(); flash("Opportunity updated.", "success")
        return redirect(url_for("opportunities.detail", opportunity_id=opportunity.id))
    return render_template("opportunities/form.html", form=form, opportunity=opportunity)

@bp.post("/<int:opportunity_id>/close")
@roles_required("client", "administrator")
def close(opportunity_id):
    if not ActionForm().validate_on_submit(): abort(400)
    opportunity = db.get_or_404(FreelanceOpportunity, opportunity_id); _ensure_manager(opportunity)
    opportunity.status = "closed"; db.session.commit(); flash("Opportunity closed.", "success")
    return redirect(url_for("opportunities.mine") if current_user.role_name == "client" else url_for("opportunities.detail", opportunity_id=opportunity.id))

def _ensure_manager(opportunity):
    if current_user.role_name != "administrator" and opportunity.client_id != current_user.id: abort(403)
def _apply_form(opportunity, form):
    opportunity.title=form.title.data.strip(); opportunity.description=form.description.data.strip(); opportunity.category=_clean(form.category.data); opportunity.budget=form.budget.data; opportunity.deadline=form.deadline.data
def _clean(value):
    return value.strip() or None if value else None
