import os
from datetime import datetime
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   abort, current_app, send_from_directory)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import TemplateForm, UploadForm, ReviewForm
from ..models import db, Template, Submission, Status, Role

bp = Blueprint("main", __name__)

# ── アップロード可能拡張子 ──────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {
        'pdf', 'xlsx', 'xls', 'csv', 'doc', 'docx', 'ppt', 'pptx'
    }

# ── ダッシュボード（共通入口）───────────────────────────────────────────
@bp.route("/")
@login_required
def dashboard():
    if current_user.role == Role.master:
        templates = Template.query.filter_by(owner_id=current_user.id).all()
        return render_template("dashboard_master.html", templates=templates)
    else:
        templates = Template.query.all()
        submissions = {s.template_id: s for s in
                       Submission.query.filter_by(client_id=current_user.id).all()}
        return render_template("dashboard_client.html",
                               templates=templates,
                               submissions=submissions,
                               Status=Status)

# ── テンプレートダウンロード（全員可）───────────────────────────────────
@bp.route("/template/<int:id>/download")
@login_required
def download_template(id):
    tmpl = Template.query.get_or_404(id)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"],
                               tmpl.filename, as_attachment=True)

# ── 静的アップロードファイル参照 ────────────────────────────────────────
@bp.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"],
                               filename, as_attachment=True)

# ── Master: テンプレート新規作成 ───────────────────────────────────────
@bp.route("/template/new", methods=["GET", "POST"])
@login_required
def new_template():
    if current_user.role != Role.master:
        abort(403)
    form = TemplateForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            fname = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], fname)
            file.save(save_path)
            tmpl = Template(
                title=form.title.data,
                description=form.description.data,
                filename=fname,
                owner_id=current_user.id
            )
            db.session.add(tmpl)
            db.session.commit()
            flash("Template created.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid file type.", "danger")
    return render_template("new_template.html", form=form)

# ── Client: 提出ファイルアップロード ───────────────────────────────────
@bp.route("/template/<int:id>/upload", methods=["GET", "POST"])
@login_required
def upload_submission(id):
    tmpl = Template.query.get_or_404(id)
    form = UploadForm()

    # Submission レコードを取得または生成
    sub = Submission.query.filter_by(template_id=id, client_id=current_user.id).first()
    if not sub:
        sub = Submission(template_id=id, client_id=current_user.id)
        db.session.add(sub)
        db.session.commit()

    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            fname = secure_filename(
                f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}"
            )
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], fname)
            file.save(save_path)

            sub.filename     = fname
            sub.status       = Status.submitted
            sub.submitted_at = datetime.utcnow()
            db.session.commit()

            flash("File uploaded.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid file type.", "danger")

    return render_template("upload.html", template=tmpl,
                           submission=sub, form=form, Status=Status)

# ── Master: 提出物レビュー & ステータス変更 ────────────────────────────
@bp.route("/submission/<int:id>/review", methods=["GET", "POST"])
@login_required
def review_submission(id):
    if current_user.role != Role.master:
        abort(403)
    sub  = Submission.query.get_or_404(id)
    tmpl = Template.query.get(sub.template_id)
    if tmpl.owner_id != current_user.id:
        abort(403)

    form = ReviewForm(status=sub.status.name if sub.status else "reviewing",
                      comment=sub.comment)

    if form.validate_on_submit():
        sub.status  = Status[form.status.data]
        sub.comment = form.comment.data
        db.session.commit()
        flash("Status updated.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("review.html", submission=sub,
                           form=form, Status=Status)
