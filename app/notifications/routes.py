from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from app.extensions import db
from app.models import Notification
from . import bp

class ActionForm(FlaskForm): pass

@bp.get("/")
@login_required
def index():
    items=db.session.scalars(db.select(Notification).where(Notification.user_id==current_user.id).order_by(Notification.created_at.desc())).all()
    return render_template("notifications/index.html",notifications=items,action_form=ActionForm())

@bp.post("/<int:notification_id>/read")
@login_required
def mark_read(notification_id):
    item=db.get_or_404(Notification,notification_id)
    if item.user_id!=current_user.id: abort(403)
    item.is_read=True; db.session.commit(); return redirect(url_for("notifications.index"))

@bp.post("/read-all")
@login_required
def mark_all_read():
    if not ActionForm().validate_on_submit(): abort(400)
    db.session.execute(db.update(Notification).where(Notification.user_id==current_user.id,Notification.is_read.is_(False)).values(is_read=True)); db.session.commit(); flash("All notifications marked as read.","success"); return redirect(url_for("notifications.index"))
