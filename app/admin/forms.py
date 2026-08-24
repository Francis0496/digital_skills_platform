from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL


DIFFICULTY_LEVELS = ("Beginner", "Intermediate", "Advanced")


class CategoryForm(FlaskForm):
    name = StringField("Category name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save category")


class CourseForm(FlaskForm):
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    title = StringField("Course title", validators=[DataRequired(), Length(max=180)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=5000)])
    difficulty_level = SelectField(
        "Difficulty",
        choices=[("", "Select difficulty")] + [(level, level) for level in DIFFICULTY_LEVELS],
        validators=[Optional()],
    )
    image = StringField("Image URL or path", validators=[Optional(), Length(max=255)])
    is_published = BooleanField("Published")
    submit = SubmitField("Save course")


class LessonForm(FlaskForm):
    title = StringField("Lesson title", validators=[DataRequired(), Length(max=180)])
    content = TextAreaField("Lesson content", validators=[DataRequired(), Length(max=20000)])
    video_url = StringField(
        "Video URL", validators=[Optional(), URL(require_tld=False), Length(max=500)]
    )
    lesson_order = IntegerField(
        "Lesson order", validators=[DataRequired(), NumberRange(min=1, max=1000)]
    )
    submit = SubmitField("Save lesson")


class ActionForm(FlaskForm):
    submit = SubmitField("Confirm")

class SkillAdminForm(FlaskForm):
    name = StringField("Skill name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save skill")
