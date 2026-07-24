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