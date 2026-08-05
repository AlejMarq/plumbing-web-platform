from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms import PasswordField, DecimalField, TextAreaField, SubmitField

from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    PasswordField,
    SubmitField,
    DateTimeLocalField
)


class ServiceRequestForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=100)]
    )

    email = StringField(
        "Email Address",
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
        "What type of service do you need?",
        choices=[
            ("", "Select a service"),
            ("Leak Detection and Repair", "Leak Detection and Repair"),
            ("Drain Cleaning and Unclogging", "Drain Cleaning and Unclogging"),
            ("Faucet or Sink Service", "Faucet or Sink Service"),
            ("Toilet Service", "Toilet Service"),
            ("Garbage Disposal Service", "Garbage Disposal Service"),
            ("Water Heater Service", "Water Heater Service"),
            ("Pipe Repair or Repiping", "Pipe Repair or Repiping"),
            (
                "Water Pressure Troubleshooting",
                "Water Pressure Troubleshooting"
            ),
            (
                "Shower or Bathtub Plumbing",
                "Shower or Bathtub Plumbing"
            ),
            (
                "Fixture Installation or Upgrade",
                "Fixture Installation or Upgrade"
            ),
            ("Remodeling Plumbing", "Remodeling Plumbing"),
            (
                "New Construction Plumbing",
                "New Construction Plumbing"
            ),
            ("Commercial Plumbing", "Commercial Plumbing"),
            (
                "Preventative Maintenance",
                "Preventative Maintenance"
            ),
            ("Emergency Plumbing", "Emergency Plumbing"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "Tell us about your project or plumbing issue",
        validators=[DataRequired(), Length(max=2000)]
    )

    submit = SubmitField("Request Service")

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

class UpdateRequestStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("New", "New"),
            ("Scheduled", "Scheduled"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Update Status")

class ScheduleAppointmentForm(FlaskForm):
    appointment_at = DateTimeLocalField(
        "Appointment",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Appointment")

class InternalNotesForm(FlaskForm):
    internal_notes = TextAreaField(
        "Internal Notes"
    )

    submit = SubmitField("Save Notes")

class EstimateForm(FlaskForm):
    labor_cost = DecimalField(
        "Labor Cost",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ],
        places=2
    )

    parts_cost = DecimalField(
        "Parts Cost",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ],
        places=2
    )

    tax_amount = DecimalField(
        "Tax Amount",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ],
        places=2
    )

    notes = TextAreaField(
        "Estimate Notes",
        validators=[Optional()]
    )

    submit = SubmitField("Save Estimate")