from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, URL

class PortfolioForm(FlaskForm):
    title = StringField("Professional headline", validators=[Optional(), Length(max=180)])
    description = TextAreaField("Portfolio introduction", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Save portfolio")

class ProjectForm(FlaskForm):
    title = StringField("Project title", validators=[DataRequired(), Length(max=180)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=5000)])
    project_image = FileField("Project image", validators=[Optional(), FileAllowed(("jpg", "jpeg", "png", "webp"), "Upload a JPG, PNG, or WebP image.")])
    project_url = StringField("Project URL", validators=[Optional(), URL(require_tld=False), Length(max=500)])
    completion_date = DateField("Completion date", validators=[Optional()])
    submit = SubmitField("Save project")

class ConfirmForm(FlaskForm):
    submit = SubmitField("Confirm")
