from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime
app = Flask(__name__)

# Configure the database URI for PostgreSQL
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://task_db_m4nd_user:40Ma9VCQ6jnyNqyGBXvvY1lMqxVi04k9@dpg-ctoo311opnds73fjflag-a.frankfurt-postgres.render.com/task_db_m4nd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disables SQLAlchemy modification tracking

# Initialize database and migration tools
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Task {self.title}>"

    @property
    def status(self):
        today = datetime.utcnow().date()  # Get the current date (ignoring time)
        deadline_date = self.deadline.date()  # Get the date part of the deadline
        if self.completed:
            return "Completed"
        elif deadline_date < today:
            return "Overdue"
        elif deadline_date == today:
            return "Due Today"
        else:
            return "Pending"

    @property
    def formatted_deadline(self):
        return self.deadline.strftime('%d %b %y')  # Format like "20 Oct 24"


@app.route('/')
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
            tasks = Task.query.filter(Task.deadline < datetime.utcnow(), Task.completed == False).order_by(Task.deadline.asc()).all()
        else:
            tasks = Task.query.filter(Task.deadline < datetime.utcnow(), Task.completed == False).order_by(Task.deadline.desc()).all()

    elif sort_by == 'today':
        # Sorting tasks that are due today
        today = datetime.utcnow().date()
        if sort_direction == 'asc':
            tasks = Task.query.filter(func.date(Task.deadline) == today, Task.completed == False).order_by(Task.deadline.asc()).all()
        else:
            tasks = Task.query.filter(func.date(Task.deadline) == today, Task.completed == False).order_by(Task.deadline.desc()).all()

    else:
        # Default sorting by deadline (ascending or descending based on direction)
        if sort_direction == 'asc':
            tasks = Task.query.order_by(Task.deadline.asc()).all()
        else:
            tasks = Task.query.order_by(Task.deadline.desc()).all()

    return render_template('index.html', tasks=tasks, sort_by=sort_by, sort_direction=sort_direction)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        deadline = request.form['deadline']

        try:
            # Parse the deadline to a datetime object (assumes format is 'YYYY-MM-DD')
            deadline = datetime.strptime(deadline, '%Y-%m-%d')
            new_task = Task(title=title, description=description, deadline=deadline)
            db.session.add(new_task)
            db.session.commit()  # Commit to save to the database
            return redirect(url_for('index'))
        except Exception as e:
            # If an error occurs during the commit, you can log it or return an error message
            print(f"Error adding task: {e}")
            return render_template('add_task.html', error="There was an issue adding the task.")

    return render_template('add_task.html')


@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()  # Commit the deletion
    except Exception as e:
        print(f"Error deleting task: {e}")
    return redirect(url_for('index'))


@app.route('/update_status/<int:id>')
def update_status(id):
    # Get the task by its ID
    task = Task.query.get_or_404(id)

    # Toggle the completed status
    task.completed = not task.completed

    # Commit the change to the database
    db.session.commit()

    # Redirect back to the index page
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
