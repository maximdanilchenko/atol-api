# -*- coding: utf-8 -*-
# REST-API сервер, сайт личного кабинета, старт flask-приложения
import os
import sys
from flask import send_file, url_for, jsonify, abort, make_response, redirect
from jinja2 import Environment, FileSystemLoader
from flask_mail import Mail, Message
from werkzeug.contrib.cache import SimpleCache
# в продакшене это должен быть мемкэш/GoogleAppEngine кэш сервер:
# http://flask.pocoo.org/docs/0.11/patterns/caching/
from Helpers import *
import Token
# from Models import User
from App import app, db

work_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.realpath(__file__))
work_dir = "%s/%s" % (work_dir.replace("\\", "/"), 'html')


"""
    -----Настройка приложения-----
    Объекты: mail, db, cache
"""
mail = Mail(app)
# db.drop_all() # раскомментить, чтобы удалить все таблицы из БД при старте приложения
# db.create_all()
cache = SimpleCache()

"""
    -----REST-API сервера-----
"""


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'success': False, 'error': 'Bad request'}), 400)


@app.errorhandler(401)
def not_auth(error):
    return make_response(jsonify({'success': False, 'error': 'Unauthorized'}), 401)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'success': False, 'error': 'Not found'}), 404)


def is_auth(fn):
    def wrapped():
        access_token, = validate_post(('access_token',), (str,), (0,)) or validate_get(('access_token',), (str,), (0,))
        if not access_token:
            abort(401)
        addr = cache.get(access_token)
        if addr and addr == user_info(request):
            cache.set(access_token, user_info(request), app.config['MAX_CACHE_TIME'])
            fn()
        else:
            abort(401)
    return wrapped


@app.route("/hub/connect", methods=['POST'])
def try_update_post():
    hub_id, = validate_post(('hub_id',), (to_int,), (0,))
    # Тут мы должны определить что это за хаб и нужно ли ему обновление, и после этого сделать нужное действие
    if hub_id:
        filename = 'C:/Users/m.danilchenko/Desktop/sw/hab19-remote/Remote/server/hub_code/Code.py'
        return send_file(filename, as_attachment=True)
    else:
        abort(404)


@app.route("/api/signup", methods=['POST'])
def signup():
    email, password, conf_password, recovery = validate_post(('email', 'password', 'conf_password', 'recovery',), (str,) * 4, ('',) * 4)
    if not (email and password and conf_password == password):
        abort(400)
    # зарегестрировать пользователя в базе, если не получается, то возвращаем ошибку
    if recovery:
        # try:
        #     user = User.query.filter_by(email=email).first()
        #     if not user:
        #         abort(401)
        # except:
        #     abort(401)
        token = Token.generate_token(password, app.config['SECRET_KEY'])
        a = url_for('recovery', token=token, email=email, _external=True)
    else:
        token = Token.generate_token(email, app.config['SECRET_KEY'])
        # user = User('', email, Token.generate_token(password, app.config['SECRET_KEY']))
        # db.session.add(user)
        # try:
        #     db.session.commit()
        # except:
        #     abort(400)
        # выслать на почту пользователя следующую ссылку для подтверждение принадлежности почты:
        a = url_for('confirm', token=token, _external=True)
    print a
    # SMTP не работает в нашей сети с компа в офисе, нужен корпоративный почтовый сервер
    # настроим на серваке уже

    # msg = Message(
    #     'Hello',
    #     sender='dmax.dev@gmail.com',
    #     recipients=
    #     ['maxalexdanilchenko@gmail.com'])
    # msg.body = "This is the email body"
    # mail.send(msg)
    return jsonify({'success': True})


@app.route("/api/signin", methods=['POST'])
def signin():
    email, password = validate_post(('email', 'password',), (str,) * 2, ('',) * 2)
    if not (email and password):
        abort(400)
    # user = User.query.filter_by(email=email).first()
    # if not user or Token.confirm_token(user.password, app.config['SECRET_KEY'], None) != password or not user.confirmed:
    #     abort(401)
    # token = Token.generate_token(user.id, app.config['SECRET_KEY'])
    # Получить обратно: user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    # cache.set(token, user_info(request), app.config['MAX_CACHE_TIME'])
    # return jsonify({'success': True, 'access_token': token})


@app.route("/confirm/<string:token>", methods=['GET'])
def confirm(token):
    # token, = validate_get(('token',), (str,), (None,))
    if token:
        email = Token.confirm_token(token, app.config['SECRET_KEY'], app.config['CONFIRM_TIME'])
        # проверить пользователя по почте в базе и пометить, что он подтвердил email
        if not email:
            abort(400)
        # user = User.query.filter_by(email=email).first()
        # if not user:
        #     abort(401)
        # user.confirmed = True
        # db.session.commit()
        return redirect(url_for('success'))
        # return jsonify({'success': True, 'email': email})


@app.route("/recovery", methods=['GET'])
def recovery():
    token, email = validate_get(('token', 'email',), (str,)*2, (None,)*2)
    if token and email:
        password = Token.confirm_token(token, app.config['SECRET_KEY'], app.config['CONFIRM_TIME'])
        # проверить пользователя по почте в базе и пометить, что он подтвердил email
        if not password:
            abort(400)
        # user = User.query.filter_by(email=email).first()
        # if not user:
        #     abort(401)
        # user.password = Token.generate_token(password, app.config['SECRET_KEY'])
        # user.confirmed = True
        # db.session.commit()
        return redirect(url_for('success'))
        # return jsonify({'success': True, 'email': email})


"""
    -----Страницы личного кабинета-----
"""
siteBasePath = "html"  # путь к шаблонам относительно запущенного приложения
env = Environment(loader=FileSystemLoader(siteBasePath))


# Страницы сайта
@app.route("/sign.html")
@app.route("/sign")
@app.route("/Sign.html")
@app.route("/Sign")
def sign():
    return env.get_template("Sign.html").render()


@app.route("/success.html")
def success():
    return env.get_template("Success.html").render()


@app.route("/index.html")
@app.route("/index")
@app.route("/Home.html")
@app.route("/Home")
@app.route("/home.html")
@app.route("/home")
@app.route("/")
def home():
    return env.get_template("Home.html").render()


# if __name__ == "__main__":
#     # app.run(host='0.0.0.0', port=80)
#     app.run()
