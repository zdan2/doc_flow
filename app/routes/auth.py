from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from ..forms import LoginForm, RegisterForm
from ..models import User, db, Role, ClientCategory

bp = Blueprint("auth", __name__)

# ── ログイン ───────────────────────────────────────────────────────────
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

# ── 新規登録 ───────────────────────────────────────────────────────────
@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email already registered", "warning")
        else:
            user = User(
                email=form.email.data.lower(),
                role=Role[form.role.data],
            )
            if user.role == Role.client:
                user.category = ClientCategory[form.category.data]
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registered. Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

# ── ログアウト ─────────────────────────────────────────────────────────
@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
