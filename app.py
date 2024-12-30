from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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


@app.route('/')
def index():
    tasks = Task.query.all()  # Get all tasks from the database
    return render_template('index.html', tasks=tasks)


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


if __name__ == "__main__":
    app.run(debug=True)
