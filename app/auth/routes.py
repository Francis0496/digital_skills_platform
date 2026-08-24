from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import PUBLIC_ROLES, Role, User
from . import bp
from .forms import LoginForm, RegistrationForm


def _is_safe_redirect(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ("http", "https") and host_url.netloc == redirect_url.netloc


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        existing_user = db.session.scalar(db.select(User).filter_by(email=email))
        role = db.session.scalar(db.select(Role).filter_by(name=form.role.data))

        if existing_user:
            form.email.errors.append("An account already uses this email address.")
        elif form.role.data not in PUBLIC_ROLES or role is None:
            form.role.errors.append("Select a valid public account type.")
        else:
            user = User(full_name=form.full_name.data.strip(), email=email, role=role)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created. You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.scalar(db.select(User).filter_by(email=email))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email address or password.", "error")
        elif not user.is_active:
            flash("This account has been deactivated. Contact an administrator.", "error")
        else:
            login_user(user, remember=form.remember_me.data)
            next_url = request.args.get("next")
            if next_url and _is_safe_redirect(next_url):
                return redirect(next_url)
            return redirect(url_for("users.dashboard"))

    return render_template("auth/login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))
