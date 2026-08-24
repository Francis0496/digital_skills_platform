from datetime import date
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

class OpportunityForm(FlaskForm):
    title = StringField("Opportunity title", validators=[DataRequired(), Length(max=180)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=10000)])
    category = StringField("Category", validators=[Optional(), Length(max=100)])
    budget = DecimalField("Budget (SLE)", places=2, validators=[Optional(), NumberRange(min=0, max=9999999999)])
    deadline = DateField("Application deadline", validators=[Optional()])
    submit = SubmitField("Save opportunity")
    def validate_deadline(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("Deadline cannot be in the past.")

class ActionForm(FlaskForm):
    submit = SubmitField("Confirm")
