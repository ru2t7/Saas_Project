from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func

from models import db, User, Task
from datetime import datetime

def register_routes(app):
    @app.route('/dashboard')
    def index():
        sort_by = request.args.get('sort_by', 'deadline')  # Default to 'deadline' if no sorting option is selected
        sort_direction = request.args.get('sort_direction', 'asc')  # Default direction to ascending if not specified

        # Get the current date for comparison
        today = datetime.utcnow().date()

        if sort_by == 'status':
            # Sorting tasks based on status priority: Overdue > Today > Pending > Completed
            case_condition = db.case(
                # Overdue: Tasks that have passed the deadline and are not completed
                ((Task.deadline < today) & (Task.completed == False), 1),
                # Due Today: Tasks whose deadline is today and not completed
                ((Task.deadline == today) & (Task.completed == False), 2),
                # Pending: Tasks that are not completed and are not overdue
                (Task.completed == False, 3),
                # Completed: Tasks that are marked as completed
                (Task.completed == True, 4),
                else_=5  # Default, catch-all for any tasks that don't match above
            )
            # Handle sorting direction (ascending or descending)
            if sort_direction == 'asc':
                tasks = Task.query.order_by(case_condition.asc(), Task.deadline.asc()).all()
            else:
                tasks = Task.query.order_by(case_condition.desc(), Task.deadline.desc()).all()

        elif sort_by == 'overdue':
            # Sorting tasks that are overdue (tasks with a past deadline and not completed)
            if sort_direction == 'asc':
                tasks = Task.query.filter(Task.deadline < datetime.utcnow(), Task.completed == False).order_by(
                    Task.deadline.asc()).all()
            else:
                tasks = Task.query.filter(Task.deadline < datetime.utcnow(), Task.completed == False).order_by(
                    Task.deadline.desc()).all()

        elif sort_by == 'today':
            # Sorting tasks that are due today
            today = datetime.utcnow().date()
            if sort_direction == 'asc':
                tasks = Task.query.filter(func.date(Task.deadline) == today, Task.completed == False).order_by(
                    Task.deadline.asc()).all()
            else:
                tasks = Task.query.filter(func.date(Task.deadline) == today, Task.completed == False).order_by(
                    Task.deadline.desc()).all()

        else:
            # Default sorting by deadline (ascending or descending based on direction)
            if sort_direction == 'asc':
                tasks = Task.query.order_by(Task.deadline.asc()).all()
            else:
                tasks = Task.query.order_by(Task.deadline.desc()).all()

        return render_template('index.html', tasks=tasks, sort_by=sort_by, sort_direction=sort_direction)

    @app.route('/', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            # If the user is already logged in, redirect them to the dashboard
            return redirect(url_for('index'))  # Change 'dashboard' to the name of your dashboard route
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.')
        return render_template('login.html')



    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('Username already exists.')
                return redirect(url_for('register'))
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully.')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_task():
        if current_user.role != 'admin':
            flash("You do not have permission to perform this action.", "error")
            return redirect(url_for('index'))

        if request.method == 'POST':
            title = request.form['title']
            description = request.form.get('description')
            deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
            new_task = Task(title=title, description=description, deadline=deadline)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('add_task.html')

    @app.route('/delete/<int:id>')
    @login_required
    def delete_task(id):
        if current_user.role != 'admin':
            flash("You do not have permission to perform this action.", "error")
            return redirect(url_for('index'))

        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('index'))

    @app.route('/update_status/<int:id>')
    @login_required
    def update_status(id):
        task = Task.query.get_or_404(id)
        task.completed = not task.completed
        db.session.commit()
        return redirect(url_for('index'))
