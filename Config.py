# -*- coding: utf-8 -*-
# Конфигурация приложения
import os
import sys

# приложение
DEBUG = True
SECRET_KEY = "\xd2\xc9\xc7\xe1\x03\xe7%\xd0\xed?z\x85\xc0\x8e\x04'LH\x142\t\x11SB"

# база данных
env = os.getenv('SERVER_SOFTWARE')

if env and env.startswith('Google App Engine/'):
    # Connecting from App Engine
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@/atol_hab?unix_socket=/cloudsql/atol-test:us-east1:cloudbd'
else:
    # Connecting from an external network.
    # Make sure your network is whitelisted
    if 'win' in sys.platform:
        SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cloudbd'
    else:
        SQLALCHEMY_DATABASE_URI = 'mysql://root@104.196.55.149:3306/cloudbd'

SQLALCHEMY_TRACK_MODIFICATIONS = False

# время, через которое удаляется кэш запись, если она не обновляется
MAX_CACHE_TIME = 24 * 60 * 60

# # почта
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 587
# MAIL_USE_SSL = True
# MAIL_USE_TLS = False
# MAIL_USERNAME = 'dmax.dev@gmail.com'
# MAIL_PASSWORD = 'password'

# время, в течение которого ссылка для подтверждения почты является действующей (confirmation token is valid)
CONFIRM_TIME = 24 * 60 * 60
