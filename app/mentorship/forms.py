from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class RequestForm(FlaskForm):
    message = TextAreaField("Message", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Send mentorship request")
class ResponseForm(FlaskForm):
    decision = RadioField("Decision", choices=[("accepted","Accept"),("rejected","Reject")], validators=[DataRequired()])
    submit = SubmitField("Save response")


class GoalForm(FlaskForm):
    title = StringField("Goal title", validators=[DataRequired(), Length(min=3, max=180)])
    description = TextAreaField(
        "Goal description", validators=[DataRequired(), Length(min=10, max=3000)]
    )
    submit = SubmitField("Create goal")


class ProgressUpdateForm(FlaskForm):
    goal_id = SelectField("Goal (optional)", coerce=int, validators=[Optional()])
    content = TextAreaField(
        "Progress update", validators=[DataRequired(), Length(min=10, max=4000)]
    )
    submit = SubmitField("Submit update")


class FeedbackForm(FlaskForm):
    progress_update_id = SelectField(
        "Progress update (optional)", coerce=int, validators=[Optional()]
    )
    goal_id = SelectField("Goal (optional)", coerce=int, validators=[Optional()])
    content = TextAreaField(
        "Mentor feedback", validators=[DataRequired(), Length(min=10, max=4000)]
    )
    submit = SubmitField("Submit feedback")


class WorkspaceActionForm(FlaskForm):
    pass
