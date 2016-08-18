# -*- coding: utf-8 -*-
# Конфигурация приложения
import os

# приложение
DEBUG = True
SECRET_KEY = os.urandom(24)

# база данных
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@/cloudbd?unix_socket=/cloudsql/atol-test:us-east1:cloudbd'
# os.environ['SQLALCHEMY_DATABASE_URI']#'mysql://root@localhost/api'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# время, через которое удаляется кэш запись, если она не обновляется
MAX_CACHE_TIME = None

# почта
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_USERNAME = 'dmax.dev@gmail.com'
MAIL_PASSWORD = 'password'

# время, в течение которого ссылка для подтверждения почты является действующей (confirmation token is valid)
CONFIRM_TIME = 24*60*60
