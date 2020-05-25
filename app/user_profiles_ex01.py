from flask import Flask, request, render_template, abort, redirect, url_for
from app.models import Person, Message
from app import db
import json
import datetime
from sqlalchemy.orm.exc import NoResultFound

from app import app

@app.route('/user', methods=['GET', 'POST'])
def user_list():
	if request.method == 'POST':
		p = Person()
		p.username = request.get_data(as_text=True)
		db.session.add(p)
		db.session.commit()
	template_context = dict(users=Person.query.all(), Message=Message, get_latest_message=get_latest_message)
	return render_template('user_list_template.html', **template_context)

@app.route('/user/<username>')
def user_profile(username):
	try:
		p = Person.query.filter_by(username=username).one()
		return render_template('user_profile_template.html', user=p)
	except NoResultFound:
		abort(404, f"User {username} not found")

@app.route('/user/<username>/color', methods=['GET','POST'])
def user_color(username):
	try:
		p = Person.query.filter_by(username=username).one()
		if request.method=='POST':
			body = request.get_data(as_text=True)
			p.color = body
			db.session.add(p)
			db.session.commit()
		if p.color:
			return p.color
		else:
			abort(404, f"User {username} does not have a favorite color")
	except NoResultFound:
		abort(404, f"User {username} not found")

@app.route('/user/<username>/mod_time')
def color_mod_time(username):
	try:
		p = Person.query.filter_by(username=username).one()
		if p.mod_time:
			return p.mod_time
		else:
			abort(404, f"User {username} does not have a mod_time")
	except NoResultFound:
		abort(404, f"User {username} not found")

@app.route('/user/<username>/messages', methods=['GET', 'POST'])
def user_messages(username):
	try:
		p = Person.query.filter_by(username=username).one()
		if  request.method == 'POST':
			post_message(p, request.get_data(as_text=True))
	except NoResultFound:
		abort(404, f"User {username} not found")
	messages_dict = dict()
	for m in p.messages.all():
		messages_dict[m.timestamp.isoformat()] = m.body
	if len(messages_dict) > 0:
		return messages_dict
	else:
		abort(404, f"User {username} has no messages")

@app.route('/user/<username>/messages/latest')
def latest_message(username):
	timestamp = get_latest_message(username).isoformat()
	return redirect(url_for(f'message', username=username, timestamp=timestamp), code=301)

@app.route('/user/<username>/messages/<timestamp>', methods=['GET', 'PUT'])
def message(username, timestamp):
	try:
		ts = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
		if request.method == 'PUT':
			m_id = put_message(username, ts, request.get_data(as_text=True))
			m = Message.query.get(m_id)
		else:
			p = Person.query.filter_by(username=username).one()
			m_exists = False
			for m in p.messages.all():
				if m.timestamp == ts:
					m_exists = True
					break
			if not m_exists:
				abort(404, "Message not found")
		return f"<p>{m.body}</p> <p>{m.timestamp}</p>"
	except ValueError:
		abort(400, f"Invalid timpstamp format")

def get_latest_message(username):
	try:
		p = Person.query.filter_by(username=username).one()
	except NoResultFound:
		abort(404, f"User {username} not found")
	try:
		maximum = p.messages.all()[0].timestamp
		for m in p.messages.all():
			if m.timestamp > maximum:
				m = maximum
		return maximum
	except IndexError:
		abort(404, f"User {username} has no messages")

def post_message(p, body):
	ts = datetime.datetime.utcnow()
	m = Message()
	m.timestamp = ts
	m.body = body
	m.person_id = p.id
	db.session.add(m)
	db.session.commit()

def put_message(username, ts, body):
	m = Message.query.filter_by(timestamp=ts).one()
	m.timestamp = ts
	m.body = body
	m.person_id = Person.query.filter_by(username=username).one().id
	db.session.add(m)
	db.session.commit()
	return m.id

def add_user(username, color):
	user = Person(username=username, color=color)
	db.session.add(user)
	db.session.commit()

@app.route('/make_coffee/')
def make_coffee():
	abort(418)
