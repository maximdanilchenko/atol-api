# -*- coding: utf-8 -*-
# Определение архитектуры базы данных
from App import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    password = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(120), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(150), unique=True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return self.email
