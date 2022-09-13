#import sqlite3
import datetime
from forms import AddTaskForm, RegisterForm, LoginForm
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flask import Flask, flash, redirect, render_template, \
    request, session, url_for, g
    
# set up app and config
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User

# helper functions

#def connect_db():
#    return sqlite3.connect(app.config['DATABASE_PATH'])
    
def hf_login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
    
def hf_flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u'Error in the %s field - %s' % (
                getattr(form, field).label.text, error), 'error')
                
def hf_open_tasks():
    return db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())
    
def hf_closed_tasks():
    return db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())
    
# route handlers

@app.route('/logout/')
@hf_login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Goodbye!')
    return redirect(url_for('login'))
    
@app.route('/', methods =['GET','POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            #if request.form['username'] != app.config['USERNAME'] \
            #  or request.form['password'] != app.config['PASSWORD']:
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['role'] = user.role
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid credentials. Please try again.'
                return render_template('login.html',form=form,error=error)
        #else:
            #error = 'Both fields are required.'
    return render_template('login.html',form=form,error=error)
    
@app.route('/tasks/')
@hf_login_required
def tasks():
    #g.db = connect_db()
    #cursor = g.db.execute('SELECT name, due_date, priority, task_id FROM tasks WHERE status=1')
    #open_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cursor.fetchall()]
    
    #cursor = g.db.execute('SELECT name, due_date, priority, task_id FROM tasks WHERE status=0')
    #closed_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cursor.fetchall()]
    #g.db.close()
    
    open_tasks = db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())
    
    closed_tasks = db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())
    
    return render_template(
        'tasks.html',
        form = AddTaskForm(request.form),
        open_tasks=hf_open_tasks(),
        closed_tasks=hf_closed_tasks())
    
@app.route('/add/', methods=['GET','POST'])
@hf_login_required
def new_task():
    #g.db = connect_db()
    #name = request.form['name']
    #due_date = request.form['due_date']
    #priority = request.form['priority']
    #if not name or not due_date or not priority:
    #    flash('All fields are required. Please try again.')
    #    return redirect(url_for('tasks'))
    #else:
    #    cursor = g.db.execute('INSERT INTO tasks(name, due_date, priority, status) VALUES(?,?,?,1)', [ 
    #        request.form['name'],
    #        request.form['due_date'],
    #        request.form['priority']
    #        ])
    #    g.db.commit()
    #    g.db.close()
    #    flash('New entry has been created.')
    #    return redirect(url_for('tasks'))
    error = None
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate():
            new_task = Task(
                        form.name.data,
                        form.due_date.data,
                        form.priority.data,
                        datetime.datetime.utcnow(),
                        '1',
                        session['user_id'])
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully added.')
            return redirect(url_for('tasks'))
        else:
            return render_template('tasks.html',form=form,
                                                error=error,
                                                open_tasks=hf_open_tasks(),
                                                closed_tasks=hf_closed_tasks()
                                    )
    return render_template('tasks.html',form=form,error=error)
        
@app.route('/complete/<int:task_id>/')
@hf_login_required
def complete(task_id):
    #g.db = connect_db()
    #g.db.execute('UPDATE tasks SET status=0 WHERE task_id='+str(task_id))
    #g.db.commit()
    #g.db.close()
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == 'admin':
        task.update({'status':'0'})
        db.session.commit()
        flash('Task has been marked complete.')
        return redirect(url_for('tasks'))
    else:
        flash('You can only update tasks that belong to you.')
        return redirect(url_for('tasks'))
    
@app.route('/delete/<int:task_id>/')
@hf_login_required
def delete_entry(task_id):
    #g.db = connect_db()
    #g.db.execute('DELETE FROM tasks WHERE task_id='+str(task_id))
    #g.db.commit()
    #g.db.close()
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == 'admin':
        task.delete()
        db.session.commit()
        flash('Task has been deleted.')
        return redirect(url_for('tasks'))
    else:
        flash('You can only delete tasks that belong to you.')
        return redirect(url_for('tasks'))
    
@app.route('/register/', methods=['GET','POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate():
            new_user = User(form.name.data,
                            form.email.data,
                            form.password.data)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login.')
                return redirect(url_for('login'))
            except IntegrityError:
                error = 'That username and/or email already exists.'
                return render_template('register.html',form=form,error=error)
    return render_template('register.html',form=form,error=error)
            
    
