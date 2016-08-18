# -*- coding: utf-8 -*-
# Конфигурация приложения
import os

# приложение
DEBUG = True
SECRET_KEY = os.urandom(24)

# база данных
env = os.getenv('SERVER_SOFTWARE')
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@/atol_hab?unix_socket=/cloudsql/atol-test:us-east1:cloudbd'
# if (env and env.startswith('Google App Engine/')):
#     # Connecting from App Engine
#     SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@/atol_hab?unix_socket=/cloudsql/atol-test:us-east1:cloudbd'
#     # os.environ['SQLALCHEMY_DATABASE_URI']#'mysql://root@localhost/api'
#     """ mysql+mysqldb://root@/<dbname>?unix_socket=/cloudsql/<projectid>:<instancename> """
# else:
#     # Connecting from an external network.
#     # Make sure your network is whitelisted
#     SQLALCHEMY_DATABASE_URI = 'mysql://root@104.196.55.149:3306/cloudbd'

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
CONFIRM_TIME = 24 * 60 * 60
