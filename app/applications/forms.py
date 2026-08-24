from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

APPLICATION_STATUSES = ("pending", "under_review", "accepted", "rejected")
class ApplicationForm(FlaskForm):
    cover_message = TextAreaField("Cover message", validators=[DataRequired(), Length(min=20, max=5000)])
    proposed_amount = DecimalField("Proposed amount", places=2, validators=[Optional(), NumberRange(min=0, max=9999999999)])
    submit = SubmitField("Submit application")
class StatusForm(FlaskForm):
    status = SelectField("Application status", choices=[(value, value.replace("_", " ").title()) for value in APPLICATION_STATUSES], validators=[DataRequired()])
    submit = SubmitField("Update status")
