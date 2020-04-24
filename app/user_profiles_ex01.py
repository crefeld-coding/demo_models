from flask import Flask, request, render_template, abort, redirect, url_for
from app.models import Person
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
	with open('user_profiles_ex01.json', 'w') as f:
		json.dump(user_profiles, f, indent=2)

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

@app.route('/user')
def user_list():
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
		try:
			if request.method == 'POST':
				body = request.get_data(as_text=True)
				user['color'] = body
				user['mod_time'] = datetime.datetime.utcnow().isoformat()
				save_profiles()
			return user['color']
		except KeyError:
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
		if request.method == 'PUT':
			put_message(username, timestamp, request.get_data(as_text=True))
		return f"<p>{user_profiles[username]['messages'][timestamp]}</p> <p>{timestamp}</p>"
	except KeyError:
		abort(404, f"Message not found")

def get_latest_message(username):
	return max(user_profiles[username]['messages'].keys())

def post_message(username, body):
	time = datetime.datetime.utcnow().isoformat()
	try:
		user_profiles[username]['messages'][time] = body
	except KeyError:
		user_profiles[username]['messages'] = {time: body}
	save_profiles()

def put_message(username, timestamp, body):
	try:
		datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f").isoformat()
	except ValueError:
		abort(400, 'Invalid timestamp format')
	user_profiles[username]['messages'][timestamp] = body
	save_profiles()

def add_user(username, color):
	user = Person(username=username, color=color)
	db.session.add(user)
	db.session.commit()

@app.route('/make_coffee/')
def make_coffee():
	abort(418)
