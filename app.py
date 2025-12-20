# FIX 1: Added 'redirect' to the list of imports here
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# Create the Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Create the database file
with app.app_context():
    db.create_all()

# The Route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        task_content = request.form.get('task_input')
        
        if task_content:
            new_task = Task(name=task_content)
            db.session.add(new_task)
            db.session.commit()
            return redirect('/') # Redirects correctly now

    # FIX 2: These lines were missing or indented wrong!
    # They must be aligned with the 'if', NOT inside it.
    all_tasks = Task.query.all()
    return render_template('index.html', tasks=all_tasks)

if __name__ == '__main__':
    app.run(debug=True)