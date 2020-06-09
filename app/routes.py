from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, MessageForm
from app.models import Person, Message
import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = Message.query.all()
    return render_template('index.html', title='Home', posts=posts, user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Person.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'), code=302)
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'), code=302)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'), code=302)

@app.route('/create', methods=['GET', 'POST'])
def create_message():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = MessageForm()
    if form.validate_on_submit():
        timestamp = datetime.datetime.utcnow()
        m = Message(body=form.body.data, timestamp=timestamp, author=current_user)
        db.session.add(m)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_message.html', title='Post a Message', form=form)
