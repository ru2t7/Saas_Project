from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# Use the db instance from app.py
from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')  # Add 'role' field

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Task {self.title}>"

    @property
    def formatted_deadline(self):
        """Format the deadline as 'DD MMM YY'."""
        return self.deadline.strftime('%d %b %y')

    @property
    def status(self):
        """Return the task's status based on deadline and completion."""
        today = datetime.utcnow().date()
        deadline_date = self.deadline.date()
        if self.completed:
            return "Completed"
        elif deadline_date < today:
            return "Overdue"
        elif deadline_date == today:
            return "Due Today"
        else:
            return "Pending"

