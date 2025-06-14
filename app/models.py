import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

# ─── 列挙型 ───────────────────────────────────────────────────────────

class Role(enum.Enum):
    master = "master"
    client = "client"

class Status(enum.Enum):
    not_submitted = "未提出"
    submitted     = "提出済み"
    reviewing     = "確認中"
    confirmed     = "確認済み"
    resubmit      = "再提出"

# ─── ユーザ ───────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role          = db.Column(db.Enum(Role), default=Role.client, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # パスワードヘルパ
    def set_password(self, password):  self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─── テンプレート（Master が登録）───────────────────────────────────────

class Template(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename    = db.Column(db.String(200), nullable=False)  # 保存パス
    owner_id    = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner       = db.relationship("User", foreign_keys=[owner_id])
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # 逆参照
    submissions = db.relationship(
        "Submission", back_populates="template",
        cascade="all, delete-orphan", lazy=True
    )

# ─── 提出物（Client がアップロード）────────────────────────────────────

class Submission(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("template.id"))
    client_id   = db.Column(db.Integer, db.ForeignKey("user.id"))

    template    = db.relationship("Template", back_populates="submissions")
    client      = db.relationship("User",   foreign_keys=[client_id])

    filename    = db.Column(db.String(200))
    status      = db.Column(db.Enum(Status), default=Status.not_submitted)
    comment     = db.Column(db.Text)
    submitted_at= db.Column(db.DateTime)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)
