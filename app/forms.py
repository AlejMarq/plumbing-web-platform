from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from wtforms import PasswordField


class ServiceRequestForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=100)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)]
    )

    phone = StringField(
        "Phone Number",
        validators=[DataRequired(), Length(max=25)]
    )

    address = StringField(
        "Service Address",
        validators=[DataRequired(), Length(max=200)]
    )

    service_type = SelectField(
        "Service Needed",
        choices=[
            ("", "Select a service"),
            ("Emergency Plumbing", "Emergency Plumbing"),
            ("Drain Cleaning", "Drain Cleaning"),
            ("Leak Repair", "Leak Repair"),
            ("Water Heater", "Water Heater"),
            ("Toilet or Faucet Repair", "Toilet or Faucet Repair"),
            ("Pipe Repair", "Pipe Repair"),
            ("Sewer Line Service", "Sewer Line Service"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "Describe the Problem",
        validators=[DataRequired(), Length(max=2000)]
    )

    submit = SubmitField("Submit Request")

class AdminLoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(max=80)]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Log In")