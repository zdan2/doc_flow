from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     TextAreaField, SelectField, FileField)
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email    = StringField("Email",    validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit   = SubmitField("Login")

class RegisterForm(FlaskForm):
    email     = StringField("Email",    validators=[DataRequired(), Email()])
    password  = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Confirm",  validators=[DataRequired(), EqualTo('password')])
    role      = SelectField("Role", choices=[("client", "Client"), ("master", "Master")])
    category  = SelectField(
        "Category",
        choices=[
            ("hoikuen", "保育園"),
            ("nintei_kodomoen", "認定こども園"),
            ("youchien", "幼稚園"),
        ],
    )
    submit    = SubmitField("Register")

class TemplateForm(FlaskForm):
    title = StringField("Title",        validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    file  = FileField("Template File",  validators=[DataRequired()])
    category = SelectField(
        "Category",
        choices=[
            ("hoikuen", "保育園"),
            ("nintei_kodomoen", "認定こども園"),
            ("youchien", "幼稚園"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Create")

class UploadForm(FlaskForm):
    file  = FileField("Upload completed file", validators=[DataRequired()])
    submit = SubmitField("Submit")

class ReviewForm(FlaskForm):
    status = SelectField("Set Status", choices=[
        ("reviewing", "確認中"),
        ("confirmed", "確認済み"),
        ("resubmit", "再提出")
    ])
    comment = TextAreaField("Comment")
    submit  = SubmitField("Update")
