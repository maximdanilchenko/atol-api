# -*- coding: utf-8 -*-
# Определение архитектуры базы данных
from App import db
from Helpers import AppException
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    recovery_token = db.Column(db.String(150))
    user_type = db.Column(db.Enum('partner', 'client'), nullable=False)

    client = db.relationship("Client", uselist=False, backref="user")
    partner = db.relationship("Partner", uselist=False, backref="user")

    def __init__(self, name, email, password, user_type):
        self.name = name
        self.email = email
        self.password = password
        self.user_type = user_type

    def __repr__(self):
        return self.email


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    hubs = db.relationship('Hub', backref='client', lazy='dynamic')


class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    hubs = db.relationship('Hub', backref='partner', lazy='dynamic')


class Hub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(150), unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
