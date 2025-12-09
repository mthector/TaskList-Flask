from flask import Flask, abort, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.task_form import TaskForm, LoginForm, RegisterForm

import config as custom_config

from databases.data import tasks, find_task, delete_task
from databases.db import db, Task, Category, User



app = Flask(__name__)
app.config.from_object(custom_config)
db.init_app(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== AUTH ROUTES ====================

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # Find user by checking email hash against all users
        users = User.query.all()
        found_user = None
        for user in users:
            if user.check_email(form.email.data):
                found_user = user
                break
        
        if found_user and found_user.check_password(form.password.data):
            login_user(found_user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        flash('Invalid email or password', 'error')
    
    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # Check if email already exists by checking all users
        users = User.query.all()
        for existing_user in users:
            if existing_user.check_email(form.email.data):
                flash('Email already registered', 'error')
                return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken', 'error')
            return render_template('register.html', form=form)
        
        # Create new user with encrypted email
        user = User(username=form.username.data)
        user.set_email(form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ==================== MAIN ROUTES ====================

@app.route('/')
@login_required
def home():
    # Show pending tasks for current user
    tasks = Task.query.filter_by(user_id=current_user.id, completed=0).order_by(Task.due_date.asc()).all()
    return render_template('all_tasks.html', tasks=tasks, view='pending')


@app.route('/completed/')
@login_required
def completed_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id, completed=1).order_by(Task.due_date.desc()).all()
    return render_template('all_tasks.html', tasks=tasks, view='completed')


@app.route('/all/')
@login_required
def all_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date.asc()).all()
    return render_template('all_tasks.html', tasks=tasks, view='all')


# ==================== TASK CRUD ====================

@app.route('/task/<int:id>/')
@login_required
def details(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()
    if task:
        return render_template('details.html', task=task)
    else:
        abort(404)


@app.route('/task/<int:id>/delete/')
@login_required
def delete(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully', 'success')
    return redirect(url_for('home'))


@app.route('/task/<int:id>/toggle/')
@login_required
def toggle_complete(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()
    if task:
        task.completed = 0 if task.completed == 1 else 1
        db.session.commit()
        flash('Task status updated', 'success')
    return redirect(url_for('home'))


@app.route('/task/<int:id>/update/', methods=["GET", "POST"])
@login_required
def update(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()
    if not task:
        abort(404)
    
    form = TaskForm(request.form, obj=task)
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]

    if form.validate() and request.method == "POST":
        task.name = form.name.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.category_id = form.category_id.data
        db.session.commit()
        flash('Task updated successfully', 'success')
        return redirect(url_for('home'))
    
    return render_template('update_task.html', form=form, task=task)


@app.route('/task/create/', methods=['GET', 'POST'])
@login_required
def create():
    form = TaskForm(request.form)
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]
    
    if form.validate() and request.method == "POST":
        task = Task(
            name=form.name.data,
            description=form.description.data,
            due_date=form.due_date.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully', 'success')
        return redirect(url_for('home'))
    
    return render_template('create_task.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)