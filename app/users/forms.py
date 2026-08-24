from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


PROFILE_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp")
PROFICIENCY_LEVELS = ("Beginner", "Intermediate", "Advanced")


class ProfileForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    location = StringField("Location", validators=[Optional(), Length(max=120)])
    bio = TextAreaField("Biography", validators=[Optional(), Length(max=2000)])
    profile_image = FileField(
        "Profile image",
        validators=[
            Optional(),
            FileAllowed(PROFILE_IMAGE_EXTENSIONS, "Upload a JPG, PNG, or WebP image."),
        ],
    )
    submit = SubmitField("Save profile")


class SkillForm(FlaskForm):
    skill_id = SelectField("Skill", coerce=int, validators=[DataRequired()])
    proficiency_level = SelectField(
        "Proficiency level",
        choices=[(level, level) for level in PROFICIENCY_LEVELS],
        validators=[DataRequired()],
    )
    submit = SubmitField("Add skill")


class MentorProfileForm(FlaskForm):
    professional_title = StringField(
        "Professional title", validators=[Optional(), Length(max=120)]
    )
    expertise = TextAreaField("Expertise", validators=[Optional(), Length(max=2000)])
    experience = TextAreaField("Experience", validators=[Optional(), Length(max=3000)])
    availability = TextAreaField("Availability", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save mentor profile")


class ConfirmForm(FlaskForm):
    submit = SubmitField("Confirm")
