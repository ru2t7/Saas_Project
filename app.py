from flask import Flask, session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, logout_user
import os

# Extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key')

    # Make session non-persistent
    @app.before_request
    def make_session_non_persistent():
        session.permanent = False  # This ensures the session is not saved across browser restarts

    @app.before_request
    def check_user_logged_in():
        if 'user_id' not in session:  # If no user is logged in, no need to do anything
            return
        if session['user_id'] and 'logged_in' in session:  # Ensure session is valid
            pass  # Proceed with your app

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://task_db_m4nd_user:40Ma9VCQ6jnyNqyGBXvvY1lMqxVi04k9@dpg-ctoo311opnds73fjflag-a.frankfurt-postgres.render.com/task_db_m4nd'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User  # Import here to avoid circular import issues
        return User.query.get(int(user_id))

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully.')
        session.clear()  # Clear the session data
        return redirect(url_for('login'))

    # Register models and routes
    with app.app_context():
        from routes import register_routes
        db.create_all()  # Ensure tables are created
        register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
