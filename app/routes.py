from flask import render_template
from app import app
from app.models import Message


@app.route('/')
@app.route('/index')
def index():
    posts = Message.query.all()
    return render_template('index.html', title='Home', posts=posts)
