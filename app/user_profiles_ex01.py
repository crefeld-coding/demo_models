from flask import Flask, request, render_template, abort, redirect, url_for
from app.models import Person, Message
from app import db
import json
import datetime
from sqlalchemy.orm.exc import NoResultFound

from app import app

def load_json():
	global user_profiles
	user_profiles = dict()
	for p in Person.query.all():
		profile = user_dict_from_model(p)
		user_profiles[p.username] = profile

def save_profiles():
	for user in user_profiles.items():
		(username, profile) = user
		if 'person_id' in profile:
			p = Person.query.get(profile['person_id'])
		else:
			p = Person()
		p.username = username
		if 'color' in profile:
			p.color = profile['color']
		db.session.add(p)
		if 'messages' in profile:
			if 'message_ids' not in profile:
				profile['message_ids'] = dict()
			for m_time in profile['messages'].keys():
				if m_time in profile['message_ids']:
					m = Message.query.get(profile['message_ids'][m_time])
				else:
					m = Message()
				m.timestamp = datetime.datetime.strptime(m_time, "%Y-%m-%dT%H:%M:%S.%f")
				m.body = profile['messages'][m_time]
				db.session.add(m)
	db.session.commit()

def user_dict_from_model(person):
	messages = dict()
	message_ids = dict()
	for message in person.messages.all():
		messages[message.timestamp.isoformat()] = message.body
		message_ids[message.timestamp.isoformat()] = message.id
	return {'color': person.color, 'messages': messages, 'person_id': person.id, 'message_ids': message_ids}

@app.before_request
def before_request():
	load_json()

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
		if p.color:
			return p.color
		else:
			abort(404, f"User {username} does not have a favorite color")
	except NoResultFound:
		abort(404, f"User {username} not found")

@app.route('/user/<username>/mod_time')
def color_mod_time(username):
	try:
		user = user_profiles[username]
		try:
			return user['mod_time']
		except KeyError:
			abort(404, f"User {username} does not have a mod_time")
	except KeyError:
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
	m = Message()
	m.timestamp = ts
	m.body = body
	m.person_id = user_profiles[username]['person_id']
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
