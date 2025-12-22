# FIX 1: Added 'redirect' to the list of imports here
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)

# Configure the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = 'thisisasecrectkey' # needed for encryption
db = SQLAlchemy(app)

# login Manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# The new user table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)


# Create the Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    # The foreign key (The link)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create the database file
with app.app_context():
    db.create_all()

# The Route
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # if they are adding a task
    if request.method == 'POST':
        task_content = request.form['content']
        # Link the task to the CURRENT
        new_task = Task(name=task_content, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    # show only task that belong to current user
    tasks = Task.query.filter_by(user_id=current_user.id)
    return render_template('index.html', tasks=tasks)
    

@app.route('/update/<int:id>')
@login_required
def update(id):
    # only find the task if it belong to the current user
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    task.complete = not task.complete
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    # only to find the task if it belong to the current user
    task_to_delete = Task.query.filter_by(id=id, user_id=current_user.id).first_or-404()
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem delecting that task'
    
@app.route('/clear')
def clear():
    # This commanddelete every single row in the debase
    db.session.query(Task).delete()
    db.session.commit()
    return redirect('/')


# --- REGISTER ROUTE---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists!"
        
        # Create new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log them in immediately
        login_user(new_user)
        return redirect('/')
    
    return render_template('register.html')

# ---LOGIN ROUTE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find the user in the database
        user = User.query.filter_by(username=username).first()
        
        # check password
        if user and user.password == password:
            login_user(user)
            return redirect('/')
        
        return "invalid username or password"
    return render_template('login.html')
# --- LOGOUT ROUTE---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')