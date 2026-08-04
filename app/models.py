from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(25), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(30), nullable=False, default="New")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    appointment_at = db.Column(db.DateTime, nullable=True)
    internal_notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<ServiceRequest {self.id}: {self.name}>"

class Estimate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    service_request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.id"),
        nullable=False,
        unique=True
    )

    labor_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    parts_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    service_request = db.relationship(
        "ServiceRequest",
        backref=db.backref(
            "estimate",
            uselist=False,
            cascade="all, delete-orphan"
        )
    )

    @property
    def total(self):
        return (
            self.labor_cost
            + self.parts_cost
            + self.tax_amount
        )

    def __repr__(self):
        return f"<Estimate {self.id} for request {self.service_request_id}>"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    service_request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.id"),
        nullable=False,
        unique=True
    )

    labor_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    parts_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    notes = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Unpaid"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    paid_at = db.Column(
        db.DateTime,
        nullable=True
    )

    service_request = db.relationship(
        "ServiceRequest",
        backref=db.backref(
            "invoice",
            uselist=False,
            cascade="all, delete-orphan"
        )
    )

    @property
    def total(self):
        return (
            self.labor_cost
            + self.parts_cost
            + self.tax_amount
        )

    def __repr__(self):
        return (
            f"<Invoice {self.id} "
            f"for request {self.service_request_id}>"
        )

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<Admin {self.username}>"

@login_manager.user_loader
def load_admin(admin_id):
    return db.session.get(Admin, int(admin_id))