from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# Use the db instance from app.py
from app import db

# User model
class User(db.Model, UserMixin):
    # Define table columns
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(150), unique=True, nullable=False)  # Unique username
    password_hash = db.Column(db.String(200), nullable=False)  # Hashed password for security
    role = db.Column(db.String(50), nullable=False, default='user')  # Role field with default value 'user'

    # Set hashed password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check hashed password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Task model
class Task(db.Model):
    # Define table columns
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(100), nullable=False)  # Task title
    description = db.Column(db.Text, nullable=True)  # Optional task description
    deadline = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Deadline with default value
    completed = db.Column(db.Boolean, default=False)  # Completion status, default is False

    # String representation of a task instance
    def __repr__(self):
        return f"<Task {self.title}>"

    @property
    def formatted_deadline(self):
        """
        Format the deadline for display.
        Example: 'DD MMM YY' -> '25 Dec 23'.
        """
        return self.deadline.strftime('%d %b %y')

    @property
    def status(self):
        """
        Determine the task's status based on the deadline and completion status.
        Possible statuses:
        - "Completed": Task is marked as completed.
        - "Overdue": Deadline is past the current date.
        - "Due Today": Deadline matches the current date.
        - "Pending": Deadline is in the future and task is not completed.
        """
        today = datetime.utcnow().date()  # Current date
        deadline_date = self.deadline.date()  # Extract date from deadline
        if self.completed:
            return "Completed"
        elif deadline_date < today:
            return "Overdue"
        elif deadline_date == today:
            return "Due Today"
        else:
            return "Pending"