from flask import Flask, session, flash, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, logout_user


import os

# Initialize extensions
db = SQLAlchemy()  # Database instance
migrate = Migrate()  # Migration tool
login_manager = LoginManager()  # Login manager for handling user sessions

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key')  # Secret key for session security

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Load database URL from .env file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking overhead
app.config['SESSION_COOKIE_SECURE'] = True  # Send cookies over HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Prevent cross-site request forgery

# Initialize extensions with the app
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect unauthorized users to the login page

# Define user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from model import User  # Import here to avoid circular import issues
    return User.query.get(int(user_id))  # Load user by ID from the database

# Configure session management
app.config['SESSION_TYPE'] = 'filesystem'  # Use server-side session storage
app.config['SESSION_PERMANENT'] = False  # Sessions are not permanent
app.config['SESSION_USE_SIGNER'] = True  # Sign session cookies to prevent tampering
Session(app)  # Initialize Flask-Session

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()  # Log out the current user
    flash('Logged out successfully.')  # Show a success message
    session.clear()  # Clear session data
    return redirect(url_for('login'))  # Redirect to the login page

# Register models and routes
with app.app_context():
    from model import User, Task  # Import models for database creation
    from controller import register_routes  # Import route registration function
    db.create_all()  # Ensure database tables are created
    register_routes(app)  # Register application routes

# Run the application
if __name__ == '__main__':
    app.run(debug=True)  # Start the Flask development server