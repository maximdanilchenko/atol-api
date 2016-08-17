#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Создание flask приложения
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config.from_object('Config')
db = SQLAlchemy(app)
