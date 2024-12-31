from flask import Flask, session, flash, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, logout_user
import os


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Create the Flask app directly
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key')

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://task_db_m4nd_user:40Ma9VCQ6jnyNqyGBXvvY1lMqxVi04k9@dpg-ctoo311opnds73fjflag-a.frankfurt-postgres.render.com/task_db_m4nd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Prevent cross-site request forgery


# Initialize extensions with the app
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Import here to avoid circular import issues
    return User.query.get(int(user_id))



app.config['SESSION_TYPE'] = 'filesystem'  # Use server-side session storage
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    session.clear()  # Clear the session data
    return redirect(url_for('login'))

# Register models and routes
with app.app_context():
    from models import User, Task
    from routes import register_routes
    db.create_all()  # Ensure tables are created
    register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
