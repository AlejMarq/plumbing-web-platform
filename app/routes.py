from flask import Blueprint, flash, redirect, render_template, url_for

from app import db
from app.forms import AdminLoginForm, ServiceRequestForm
from app.models import Admin, ServiceRequest

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

    return render_template(
        "admin_dashboard.html",
        service_requests=service_requests
    )

@main.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("main.admin_login"))

@main.route("/admin/requests/<int:request_id>")
@login_required
def admin_request_detail(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    return render_template(
        "admin_request_detail.html",
        service_request=service_request
    )