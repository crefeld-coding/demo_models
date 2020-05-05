from flask import Flask, request, render_template, abort, redirect, url_for
from app.models import Person, Message
from app import db
import json
import datetime

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
		user_profiles[request.get_data(as_text=True)] = dict()
		save_profiles()
	template_context = dict(users=user_profiles, get_latest_message=get_latest_message)
	return render_template('user_list_template.html', **template_context)

@app.route('/user/<username>')
def user_profile(username):
	try:
		user = user_profiles[username]
		return render_template('user_profile_template.html', username=username, user=user)
	except KeyError:
		abort(404, f"User {username} not found")

@app.route('/user/<username>/color', methods=['GET','POST'])
def user_color(username):
	try:
		user = user_profiles[username]
		if user['color']:
			if request.method == 'POST':
				body = request.get_data(as_text=True)
				user['color'] = body
				user['mod_time'] = datetime.datetime.utcnow().isoformat()
				save_profiles()
			return user['color']
		else:
			abort(404, f"User {username} does not have a favorite color")
	except KeyError:
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
	if  request.method == 'POST':
		post_message(username, request.get_data(as_text=True))
	try:
		return user_profiles[username]['messages']
	except KeyError:
		abort(404, f"User {username} has no messages")

@app.route('/user/<username>/messages/latest')
def latest_message(username):
	timestamp = get_latest_message(username)
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
	return max(user_profiles[username]['messages'].keys())

def post_message(username, body):
	time = datetime.datetime.utcnow().isoformat()
	try:
		user_profiles[username]['messages'][time] = body
	except KeyError:
		user_profiles[username]['messages'] = {time: body}
	save_profiles()

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
