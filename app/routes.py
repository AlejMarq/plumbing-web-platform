from flask import Blueprint, flash, redirect, render_template, url_for

from app import db
from app.models import Admin, ServiceRequest, Estimate
from flask import request

from flask_mail import Message
from app import mail
from flask import send_file
from flask import current_app

from app.pdf_utils import (
    create_estimate_pdf,
    create_invoice_pdf,
    send_estimate_email,
    send_invoice_email,
)

import calendar
from datetime import datetime
from app.models import Admin, Estimate, Invoice, ServiceRequest

from app.forms import (
    ServiceRequestForm,
    AdminLoginForm,
    UpdateRequestStatusForm,
    ScheduleAppointmentForm,
    InternalNotesForm,
    EstimateForm
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/request-service", methods=["GET", "POST"])
def request_service():
    form = ServiceRequestForm()

    if form.validate_on_submit():
        service_request = ServiceRequest(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            service_type=form.service_type.data,
            description=form.description.data,
        )

        db.session.add(service_request)
        db.session.commit()

        message = Message(
            subject="Service Request Received",
            recipients=[service_request.email],
        )

        message.body = f"""
        Hi {service_request.name},

        Thank you for contacting The Go To Plumber.

        We received your service request for:
        {service_request.service_type}

        Your request has been added to our system, and we will contact you soon to discuss the next steps.

        Request details:
        Phone: {service_request.phone}
        Address: {service_request.address}

        Description:
        {service_request.description}

        Thank you,
        The Go To Plumber
        """

        try:
            mail.send(message)
        except Exception as error:
            print(f"Confirmation email failed: {error}")

        flash(
            "Your service request was submitted successfully.",
            "success"
        )

        return redirect(url_for("main.request_service"))

    return render_template(
        "request_service.html",
        form=form
    )

@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("main.admin_dashboard"))

    form = AdminLoginForm()

    if form.validate_on_submit():
        admin = Admin.query.filter_by(
            username=form.username.data
        ).first()

        if admin and admin.check_password(form.password.data):
            login_user(admin)

            flash("You are now logged in.", "success")
            return redirect(url_for("main.admin_dashboard"))

        flash("Invalid username or password.", "error")

    return render_template(
        "admin_login.html",
        form=form
    )

@main.route("/admin")
@login_required
def admin_dashboard():
    service_requests = ServiceRequest.query.order_by(
        ServiceRequest.created_at.desc()
    ).all()

    total_requests = ServiceRequest.query.count()

    new_requests = ServiceRequest.query.filter_by(
        status="New"
    ).count()

    scheduled_requests = ServiceRequest.query.filter_by(
        status="Scheduled"
    ).count()

    completed_requests = ServiceRequest.query.filter_by(
        status="Completed"
    ).count()

    upcoming_jobs = (
        ServiceRequest.query
        .filter(
            ServiceRequest.appointment_at.isnot(None),
            ServiceRequest.appointment_at >= datetime.now()
        )
        .order_by(ServiceRequest.appointment_at.asc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin_dashboard.html",
        service_requests=service_requests,
        total_requests=total_requests,
        new_requests=new_requests,
        scheduled_requests=scheduled_requests,
        completed_requests=completed_requests,
        upcoming_jobs=upcoming_jobs
    )

@main.route("/admin/calendar")
@login_required
def admin_calendar():
    today = datetime.today()

    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    scheduled_requests = (
        ServiceRequest.query
        .filter(ServiceRequest.appointment_at.isnot(None))
        .order_by(ServiceRequest.appointment_at.asc())
        .all()
    )

    appointments_by_day = {}

    for service_request in scheduled_requests:
        appointment = service_request.appointment_at

        if appointment.year == year and appointment.month == month:
            appointments_by_day.setdefault(appointment.day, []).append(
                service_request
            )

    month_calendar = calendar.monthcalendar(year, month)

    previous_month = month - 1
    previous_year = year

    if previous_month == 0:
        previous_month = 12
        previous_year -= 1

    next_month = month + 1
    next_year = year

    if next_month == 13:
        next_month = 1
        next_year += 1

    return render_template(
        "admin_calendar.html",
        month_calendar=month_calendar,
        month_name=calendar.month_name[month],
        year=year,
        appointments_by_day=appointments_by_day,
        previous_month=previous_month,
        previous_year=previous_year,
        next_month=next_month,
        next_year=next_year,
        today=today
    )

@main.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("main.admin_login"))

@main.route(
    "/admin/requests/<int:request_id>",
    methods=["GET", "POST"]
)
@login_required
def admin_request_detail(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    status_form = UpdateRequestStatusForm(prefix="status")
    appointment_form = ScheduleAppointmentForm(prefix="appointment")
    notes_form = InternalNotesForm(prefix="notes")
    estimate_form = EstimateForm(prefix="estimate")

    if status_form.submit.data and status_form.validate_on_submit():
        previous_status = service_request.status
        service_request.status = status_form.status.data
        db.session.commit()

        if (
            service_request.status == "Completed"
            and previous_status != "Completed"
        ):
            message = Message(
                subject="Your Plumbing Service Is Complete",
                recipients=[service_request.email],
            )

            message.body = f"""
    Hi {service_request.name},

    Your service request for {service_request.service_type} has been marked as completed.

    Thank you for choosing The Go To Plumber.

    If you have any questions or need additional service, please contact us.

    Thank you,
    The Go To Plumber
    """

            try:
                mail.send(message)
            except Exception as error:
                print(f"Completion email failed: {error}")

        flash("Request status updated successfully.", "success")

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    if (
        appointment_form.submit.data
        and appointment_form.validate_on_submit()
    ):
        service_request.appointment_at = appointment_form.appointment_at.data
        service_request.status = "Scheduled"
        db.session.commit()

        formatted_appointment = service_request.appointment_at.strftime(
            "%B %d, %Y at %I:%M %p"
        )

        message = Message(
            subject="Your Plumbing Appointment Has Been Scheduled",
            recipients=[service_request.email],
        )

        message.body = f"""
    Hi {service_request.name},

    Your plumbing appointment has been scheduled.

    Appointment:
    {formatted_appointment}

    Service:
    {service_request.service_type}

    Address:
    {service_request.address}

    If you need to reschedule, please contact us.

    Thank you,
    The Go To Plumber
    """

        try:
            mail.send(message)
        except Exception as error:
            print(f"Appointment email failed: {error}")

        flash("Appointment scheduled successfully.", "success")

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    if notes_form.submit.data and notes_form.validate_on_submit():
        service_request.internal_notes = notes_form.internal_notes.data
        db.session.commit()

        flash("Internal notes saved successfully.", "success")

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    if request.method == "GET":
        status_form.status.data = service_request.status
        appointment_form.appointment_at.data = service_request.appointment_at
        notes_form.internal_notes.data = service_request.internal_notes

    if estimate_form.validate_on_submit():
        estimate = service_request.estimate

        if estimate is None:
            estimate = Estimate(service_request=service_request)
            db.session.add(estimate)

        estimate.labor_cost = estimate_form.labor_cost.data
        estimate.parts_cost = estimate_form.parts_cost.data
        estimate.tax_amount = estimate_form.tax_amount.data
        estimate.notes = estimate_form.notes.data

        db.session.commit()

        flash("Estimate saved successfully.", "success")

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    if request.method == "GET" and service_request.estimate:
        estimate_form.labor_cost.data = service_request.estimate.labor_cost
        estimate_form.parts_cost.data = service_request.estimate.parts_cost
        estimate_form.tax_amount.data = service_request.estimate.tax_amount
        estimate_form.notes.data = service_request.estimate.notes

    return render_template(
        "admin_request_detail.html",
        service_request=service_request,
        status_form=status_form,
        appointment_form=appointment_form,
        notes_form=notes_form,
        estimate_form=estimate_form
    )

@main.route("/admin/requests/<int:request_id>/estimate/pdf")
@login_required
def generate_estimate_pdf(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.estimate is None:
        flash(
            "Please save an estimate before generating a PDF.",
            "warning"
        )

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    filepath = create_estimate_pdf(service_request)

    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"estimate_{service_request.id}.pdf"
    )

@main.route("/admin/requests/<int:request_id>/estimate/email", methods=["POST"])
@login_required
def email_estimate(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.estimate is None:
        flash(
            "Please save an estimate before emailing it.",
            "warning"
        )

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    try:
        send_estimate_email(service_request)

        flash(
            f"Estimate emailed successfully to {service_request.email}.",
            "success"
        )

    except Exception as error:
        current_app.logger.exception(
            "Failed to email estimate for request %s",
            service_request.id
        )

        flash(
            f"Estimate could not be emailed: {error}",
            "danger"
        )

    return redirect(
        url_for(
            "main.admin_request_detail",
            request_id=service_request.id
        )
    )

@main.route(
    "/admin/requests/<int:request_id>/invoice/create",
    methods=["POST"]
)
@login_required
def create_invoice(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.estimate is None:
        flash(
            "Please save an estimate before creating an invoice.",
            "warning"
        )

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    if service_request.invoice is not None:
        flash(
            "An invoice already exists for this request.",
            "warning"
        )

        return redirect(
            url_for(
                "main.admin_request_detail",
                request_id=service_request.id
            )
        )

    estimate = service_request.estimate

    invoice = Invoice(
        service_request=service_request,
        labor_cost=estimate.labor_cost,
        parts_cost=estimate.parts_cost,
        tax_amount=estimate.tax_amount,
        notes=estimate.notes,
        status="Unpaid"
    )

    db.session.add(invoice)
    db.session.commit()

    flash(
        "Invoice created successfully from the estimate.",
        "success"
    )

    return redirect(
        url_for(
            "main.admin_request_detail",
            request_id=service_request.id
        )
    )

@main.route("/admin/invoices/<int:invoice_id>")
@login_required
def invoice_detail(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    return render_template(
        "invoice_detail.html",
        invoice=invoice
    )

@main.route("/admin/invoices/<int:invoice_id>/pdf")
@login_required
def generate_invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    filepath = create_invoice_pdf(invoice)

    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"invoice_{invoice.id}.pdf"
    )

@main.route(
    "/admin/invoices/<int:invoice_id>/email",
    methods=["POST"]
)
@login_required
def email_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    try:
        send_invoice_email(invoice)

        flash(
            f"Invoice emailed successfully to "
            f"{invoice.service_request.email}.",
            "success"
        )

    except Exception as error:
        current_app.logger.exception(
            "Failed to email invoice %s",
            invoice.id
        )

        flash(
            f"Invoice could not be emailed: {error}",
            "danger"
        )

    return redirect(
        url_for(
            "main.invoice_detail",
            invoice_id=invoice.id
        )
    )

@main.route(
    "/admin/invoices/<int:invoice_id>/toggle-paid",
    methods=["POST"]
)
@login_required
def toggle_invoice_paid(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    if invoice.status == "Paid":
        invoice.status = "Unpaid"
        invoice.paid_at = None

        flash(
            "Invoice marked as unpaid.",
            "success"
        )
    else:
        invoice.status = "Paid"
        invoice.paid_at = datetime.utcnow()

        flash(
            "Invoice marked as paid.",
            "success"
        )

    db.session.commit()

    return redirect(
        url_for(
            "main.invoice_detail",
            invoice_id=invoice.id
        )
    )