from datetime import datetime
from app import db
from flask_login import UserMixin


class Person(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    color = db.Column(db.String(64), index=True)
    mod_time = db.Column(db.DateTime, index=True)
    messages = db.relationship('Message', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Person {}>'.format(self.username)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    def __repr__(self):
        return '<Message {}>'.format(self.body)
