# -*- coding: utf-8 -*-
# Конфигурация приложения
import os
import sys

# приложение
DEBUG = True
TEST_HUB_NUM = 100
# база данных
env = os.getenv('SERVER_SOFTWARE')

if env and env.startswith('Google App Engine/'):
    # Connecting from App Engine
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@/atol_hab?unix_socket=/cloudsql/atol-test:us-east1:cloudbd1'
else:
    # Connecting from an external network.
    # Make sure your network is whitelisted
    if 'win' in sys.platform:
        SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cloudbd'
    else:
        SQLALCHEMY_DATABASE_URI = 'mysql://root@104.196.55.149:3306/cloudbd1'

SQLALCHEMY_TRACK_MODIFICATIONS = False

with open('key.secret') as key:
    SECRET_KEY = key.readline()
# время, через которое удаляется кэш запись, если она не обновляется
MAX_CACHE_TIME = 24 * 60 * 60

# # почта (если сервер - не Google App Engine)
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 587
# MAIL_USE_SSL = True
# MAIL_USE_TLS = False
# MAIL_USERNAME = 'dmax.dev@gmail.com'
# MAIL_PASSWORD = 'password'

# время, в течение которого ссылка для подтверждения почты
# является действующей (confirmation token is valid)
CONFIRM_TIME = 24 * 60 * 60

PROJECT_ID = 'atol-test'
