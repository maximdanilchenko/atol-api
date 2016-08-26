# -*- coding: utf-8 -*-
# Определение архитектуры базы данных
from App import db
from Helpers import AppException
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    # hubs = db.relationship('Hub', backref='client', lazy='dynamic')
    group = db.relationship('Client_group', backref='client', uselist=False)

    def __init__(self, user):
        self.user = user


class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    # hubs = db.relationship('Hub', backref='partner', lazy='dynamic')
    group = db.relationship('Partner_group', backref='partner', uselist=False)

    def __init__(self, user):
        self.user = user


class Client_group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    parent_id = db.Column(db.Integer, db.ForeignKey(id))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), unique=True)

    childes = db.relationship('Client_group', cascade="all", backref=db.backref('parent', remote_side=id), lazy='dynamic')
    hubs = db.relationship('Hub', backref='client_group', lazy='dynamic')

    def __init__(self, name, parent=None, client=None):
        self.name = name
        self.parent = parent
        if client:
            self.partner = client


class Partner_group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    parent_id = db.Column(db.Integer, db.ForeignKey(id))
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'), unique=True)

    childes = db.relationship('Partner_group', cascade="all", backref=db.backref('parent', remote_side=id), lazy='dynamic')
    hubs = db.relationship('Hub', backref='partner_group', lazy='dynamic')

    def __init__(self, name, parent=None, partner=None):
        self.name = name
        self.parent = parent
        if partner:
            self.partner = partner


class Hub_meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    hub = db.relationship("Hub", uselist=False, backref="hub_meta")


class Hub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(20))
    partner_name = db.Column(db.String(20))
    hub_meta_id = db.Column(db.Integer, db.ForeignKey('hub_meta.id'), unique=True)
    device_id = db.Column(db.String(150), unique=True, nullable=False)
    # client_id = db.Column(db.Integer, db.ForeignKey('client.id'), unique=True)
    # partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'), unique=True)
    client_group_id = db.Column(db.Integer, db.ForeignKey('client_group.id'))
    partner_group_id = db.Column(db.Integer, db.ForeignKey('partner_group.id'))

    def __init__(self, device_id, client_name=None, partner_name=None):
        self.device_id = device_id
        self.client_name = client_name
        self.partner_name = partner_name
