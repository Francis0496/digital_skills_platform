from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class RequestForm(FlaskForm):
    message = TextAreaField("Message", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Send mentorship request")
class ResponseForm(FlaskForm):
    decision = RadioField("Decision", choices=[("accepted","Accept"),("rejected","Reject")], validators=[DataRequired()])
    submit = SubmitField("Save response")
