# -*- coding: utf-8 -*-
# REST-API сервер, сайт личного кабинета, старт flask-приложения
import os
import sys
from flask import send_file, url_for, jsonify, abort, make_response, redirect
from jinja2 import Environment, FileSystemLoader
from functools import wraps
from Helpers import *
import Token
from Models import User, Partner, Client, Hub, Hub_meta, Client_group, Partner_group
from App import app, db
on_gae = True
try:
    from google.appengine.api import mail
except:
    on_gae = False
# from flask_mail import Mail
# mail = Mail(app)

# рабочая директория
work_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.realpath(__file__))
work_dir = "%s/%s" % (work_dir.replace("\\", "/"), 'html')

# html тело писем для отправки
MAIL_HTML_REG = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="http://www.w3schools.com/lib/w3.css">
    <link rel="stylesheet" href="http://www.w3schools.com/lib/w3-theme-red.css">
    <link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.3.0/css/font-awesome.min.css">
</head>
<body>
<header>
</header>
<div class="w3-row-padding w3-center w3-margin-top">
    <div>
        <img src="https://atol-test.appspot.com/static/img/logo.png" alt="АТОЛ" width="130" height="35">
        <h1>Поздравляем!</h1>
        <p>Регистрация в личном кабинете ATOL почти завершена</p>
        <a href={}>Пройдите по этой ссылке для завершения регистрации</a>
    </div>
</div>
</body>
</html>"""

MAIL_HTML_REC = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="http://www.w3schools.com/lib/w3.css">
    <link rel="stylesheet" href="http://www.w3schools.com/lib/w3-theme-red.css">
    <link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.3.0/css/font-awesome.min.css">
</head>
<body>
<header>
</header>
<div class="w3-row-padding w3-center w3-margin-top">
    <div>
        <img src="https://atol-test.appspot.com/static/img/logo.png" alt="АТОЛ" width="130" height="35">
        <h1>Изменение пароля</h1>
        <p>Изменение пароля личного кабинета ATOL почти завершено</p>
        <a href={}>Пройдите по этой ссылке для изменения пароля</a>
    </div>
</div>
</body>
</html>"""


"""
    -----Настройка приложения-----
    Объекты: db, cache
"""
# db.drop_all()  # раскомментить, чтобы удалить все таблицы из БД при старте приложения
db.create_all()
# задаем кэширование в зависимости от платформы запуска
from werkzeug.contrib.cache import GAEMemcachedCache, SimpleCache
if 'win' in sys.platform:
    cache = SimpleCache()
else:
    cache = GAEMemcachedCache()

"""
    -----REST-API сервера-----
"""


# обработчики ошибок
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
    """
    декоратор для проверки аутентификации методов API
    """
    @wraps(fn)
    def wrapped(*args, **kwargs):
        access_token, = validate_post(('access_token',), (str,), (0,))
        if not access_token:
            access_token, = validate_get(('access_token',), (str,), (0,))
        if not access_token:
            abort(401)
        addr = cache.get(access_token)
        if addr and addr == user_info(request):
            cache.set(access_token, user_info(request), app.config['MAX_CACHE_TIME'])
            return fn(*args, **kwargs)
        else:
            abort(401)
    return wrapped


def validate_user(access_token):
    if not access_token:
        abort(401)
    user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    user = User.query.filter_by(id=user_id).first()
    if not (user and user.user_type):
        abort(400)
    return user

@app.route("/hub/connect", methods=['POST'])
def try_update_post():
    """
    метод для подключения к хабу. Если идентификатор соответсвтует хабу, который нужно обновить,
    то на хаб отправляется скрипт для запуска
    :return:
    """
    hub_id, = validate_post(('hub_id',), (to_int,), (0,))
    # Тут мы должны определить что это за хаб и нужно ли ему обновление, и после этого сделать нужное действие
    if hub_id:
        filename = 'C:/Users/m.danilchenko/Desktop/sw/hab19-remote/Remote/server/hub_code/Code.py'
        return send_file(filename, as_attachment=True)
    else:
        abort(404)


@app.route("/api/recovery", methods=['POST'])
def api_recovery():
    """
    Вызывается для того, чтобы на почту отправить ссылку на страницу для замены пароля.
    В базе сохраняется токен для валидации пользователся по ссылке
    , который в дальнейшем удаляется после смены пароля пользователем.
    :return:
    """
    email, = validate_post(('email',),(str,), ('',))
    if not email:
        abort(400)
    token = Token.generate_token(email, app.config['SECRET_KEY'])
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            abort(401)
        user.recovery_token = token
        db.session.commit()
    except:
        abort(401)
    a = url_for('recovery', token=token, _external=True)
    print a
    mail_subject = 'Замена пароля'
    mail_body = """Пройдите по ссылке для замены пароля:
            %s""" % a
    mail_html_body = MAIL_HTML_REC.format(a)
    mail_to = email
    mail_from = 'dmax.dev@gmail.com'
    if on_gae:
        mail.send_mail(sender=mail_from,
                       to=mail_to,
                       subject=mail_subject,
                       body=mail_body,
                       html=mail_html_body)
    return jsonify({'success': True})


@app.route("/api/signup", methods=['POST'])
def api_signup():
    """
    Регистрация пользователя. Требуются почта и два поля пароля. Пользователь сохраняется в базе
    и на его почту высылается ссылка для подтверждения адреса почты. Если пользователь не подтвердил
    почту, то он может ещй раз зарегестрироваться.
    :return:
    """
    email, password, conf_password, user_type = validate_post(('email', 'password', 'conf_password', 'type'), (str,) * 4, ('',) * 4)
    if not (email and user_type and password and conf_password == password):
        abort(400)
    token = Token.generate_token(email, app.config['SECRET_KEY'])
    user = User.query.filter_by(email=email, confirmed=False, user_type=user_type).first()
    if not user:
        user = User('', email, Token.generate_token(password, app.config['SECRET_KEY']), user_type)
        if user_type == 'client':
            client = Client(user)
            db.session.add(client)
        elif user_type == 'partner':
            partner = Partner(user)
            db.session.add(partner)
        else:
            abort(400)
        db.session.add(user)
    db.session.commit()
    try:
        db.session.commit()
    except:
        abort(400)
    if user.email == 'maxalexdanilchenko@gmail.com':
        testdata()
    a = url_for('api_confirm', token=token, _external=True)
    print a
    mail_subject = 'Регистрация'
    mail_body = """Поздравляем!
    Пройдите по ссылке для завершения регистрации:
    %s""" % a
    mail_html_body = MAIL_HTML_REG.format(a)
    mail_to = email
    mail_from = 'dmax.dev@gmail.com'
    if on_gae:
        mail.send_mail(sender=mail_from,
                       to=mail_to,
                       subject=mail_subject,
                       body=mail_body,
                       html=mail_html_body)
    return jsonify({'success': True})


@app.route("/api/signin", methods=['POST'])
def api_signin():
    """
    Вход. ищется пользователь с данной почтой и проверяется его пароль.
    Если все хорошо, то возвращается access_token, который генерируется на основе
    id пользователя, а в кэше запоминается информация об устройстве/браузере/ip пользователя.
    :return:
    """
    email, password = validate_post(('email', 'password',), (str,) * 2, ('',) * 2)
    if not (email and password):
        abort(400)
    user = User.query.filter_by(email=email).first()
    if not user or Token.confirm_token(user.password, app.config['SECRET_KEY'], None) != password or not user.confirmed:
        abort(401)
    token = Token.generate_token(user.id, app.config['SECRET_KEY'])
    # Получить обратно: user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    cache.set(token, user_info(request), app.config['MAX_CACHE_TIME'])
    user.recovery_token = ''
    db.session.commit()
    return jsonify({'success': True, 'access_token': token})


@app.route("/api/newpas", methods=['POST'])
def api_newpas():
    """
    Меняет пароль пользователя, а потом регистрирует его и возвращает access_token
    :return:
    """
    token, password, conf_password = validate_post(('token', 'password', 'conf_password',), (str,) * 3, ('',) * 3)
    if not (token and password and conf_password == password):
        abort(400)
    # email = Token.confirm_token(token, app.config['SECRET_KEY'], None)
    user = User.query.filter_by(recovery_token=token).first()
    if not user:
        abort(401)
    user.password = Token.generate_token(password, app.config['SECRET_KEY'])
    user.recovery_token = ''
    user.confirmed = True
    db.session.commit()
    # Получить обратно: user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    in_token = Token.generate_token(user.id, app.config['SECRET_KEY'])
    cache.set(in_token, user_info(request), app.config['MAX_CACHE_TIME'])
    return jsonify({'success': True, 'access_token': token})


@app.route("/confirm/<string:token>", methods=['GET'])
def api_confirm(token):
    """
    поддверждения адреса почты, происходит пометка в БД, что пользователь подтвержден, после чего он может войти
    Происходит редирект на страницу успеха
    :param token:
    :return:
    """
    if token:
        email = Token.confirm_token(token, app.config['SECRET_KEY'], app.config['CONFIRM_TIME'])
        # проверить пользователя по почте в базе и пометить, что он подтвердил email
        if not email:
            abort(400)
        user = User.query.filter_by(email=email).first()
        if not user:
            abort(401)
        user.confirmed = True
        db.session.commit()
        return redirect(url_for('success'))


@app.route("/recovery/<string:token>", methods=['GET'])
def recovery(token):
    """

    :param token:
    :return:
    """
    if token:
        # email = Token.confirm_token(token, app.config['SECRET_KEY'], app.config['CONFIRM_TIME'])
        # проверить пользователя по почте в базе и пометить, что он подтвердил email
        # if not email:
        #     abort(400)
        user = User.query.filter_by(recovery_token=token).first()
        if not user:
            abort(401)
        return redirect(url_for('newpassword', email=user.email, token=token))


@app.route("/api/get_user_info", methods=['GET'])
@is_auth
def get_info():
    access_token, = validate_get(('access_token',), (str,), (0,))
    addr = cache.get(access_token)
    if not access_token:
        abort(401)
    user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    user = User.query.filter_by(id=user_id).first()
    name = user.name or user.email
    return jsonify({'success': True, 'name': name[:25], 'type': user.user_type})


@app.route("/api/get_tree", methods=['POST'])
@is_auth
def get_tree():
    access_token, = validate_post(('access_token',), (str,), (0,))
    user = validate_user(access_token)
    tree = {}
    if user.user_type == 'client':
        tree = get_tree(user.client.group, 'client')
        tr = {}
        tr[tree[0]] = tree[1]
        return jsonify(tr)
    elif user.user_type == 'partner':
        tree = get_tree(user.partner.group, 'partner')
        tr = {}
        tr[tree[0]] = tree[1]
        return jsonify(tr)


@app.route("/api/connect_hub", methods=['POST'])
@is_auth
def connect_hub():
    access_token, device_id = validate_post(('access_token', 'device_id',), (str,)*2, (0,)*2)
    if not access_token and device_id:
        abort(401)
    user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    user = User.query.filter_by(id=user_id).first()
    device = Hub.query.filter_by(device_id=device_id).first()
    if not (user and user.user_type and device):
        abort(400)
    if user.user_type == 'client':
        user.client.hubs.append(device)
    elif user.user_type == 'partner':
        user.partner.hubs.append(device)
    db.session.commit()
    return jsonify({'success': True})


@app.route("/api/disconnect_hub", methods=['POST'])
@is_auth
def disconnect_hub():
    access_token, device_id = validate_post(('access_token', 'device_id',), (str,)*2, (0,)*2)
    if not access_token and device_id:
        abort(401)
    user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    user = User.query.filter_by(id=user_id).first()
    device = Hub.query.filter_by(device_id=device_id).first()
    if not (user and user.user_type and device):
        abort(400)
    try:
        if user.user_type == 'client':
            user.client.hubs.remove(device)
        elif user.user_type == 'partner':
            user.partner.hubs.remove(device)
    except:
        abort(400)
    db.session.commit()
    return jsonify({'success': True})

"""
    -----Страницы личного кабинета-----
"""
siteBasePath = "html"  # путь к шаблонам относительно запущенного приложения
env = Environment(loader=FileSystemLoader(siteBasePath))


# Страницы сайта
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


@app.route("/signin.html")
@app.route("/signin")
def signin():
    return env.get_template("signin.html").render()


@app.route("/signup.html")
@app.route("/signup")
def signup():
    return env.get_template("signup.html").render()


@app.route("/recover.html")
@app.route("/recover")
def recover():
    return env.get_template("recover.html").render()


@app.route("/newpassword.html")
@app.route("/newpassword")
def newpassword():
    email, token = validate_get(('email', 'token',), (str,) * 2, ('',) * 2)
    return env.get_template("newpassword.html").render(email=email, token=token)


def testdata():
    user = User.query.filter_by(email='maxalexdanilchenko@gmail.com', user_type='partner').first()
    partner = user.partner

    new_group = Partner_group('group1', partner=partner)

    print new_group.partner.user

    hub1 = Hub('hub1')
    hub2 = Hub('hub2')
    hub3 = Hub('hub3')
    hub4 = Hub('hub4')
    hub5 = Hub('hub5')

    new_sub_group = Partner_group('group2', parent=new_group)
    new_sub_sub_group = Partner_group('group3', parent=new_sub_group)


    db.session.add_all([hub1, hub2, hub3, hub4, hub5, new_group, new_sub_group, new_sub_sub_group])
    db.session.commit()

    new_group.hubs.extend([hub1, hub2])
    new_sub_group.hubs.extend([hub3, hub4])
    new_sub_sub_group.hubs.extend([hub5])
    db.session.commit()

    tree = get_tree(new_group, 'partner')
    tr = {}
    tr[tree[0]] = tree[1]
    print jsonify(tr)


def get_tree(node, user_type):
    if user_type not in ('partner', 'client'):
        return None
    children = node.childes
    children_dict = dict(get_tree(child, user_type) for child in children if children)
    return (node.id, {"name": node.name,
                      "hubs": [{"id": hub.id,
                                "name": hub.partner_name if user_type == 'partner' else hub.client_name} for hub in node.hubs],
                      "children": children_dict})


env_serv = os.getenv('SERVER_SOFTWARE')

if not (env_serv and env_serv.startswith('Google App Engine/')):
    if 'win' in sys.platform and __name__ == "__main__":
        app.run()

