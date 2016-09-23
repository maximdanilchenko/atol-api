# -*- coding: utf-8 -*-
# API сервер, сайт личного кабинета, старт flask-приложения
import uuid
import os
import sys
import datetime
import time
from flask import send_file, url_for, jsonify, abort, \
    make_response, redirect, request, current_app
from jinja2 import Environment, FileSystemLoader
from functools import wraps
from Helpers import *
import Token
from Models import User, Partner, Client, Hub, \
    Client_group, Partner_group, Hub_meta, Hub_statistics, Hub_settings, \
    Hub_partner, Hub_client
from App import app, db
from sqlalchemy import desc, asc
from sqlalchemy.sql.expression import func
on_gae = True
try:
    from google.appengine.api import mail
except ImportError:
    on_gae = False
# from flask_mail import Mail
# mail = Mail(app)

# рабочая директория
work_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) \
    else os.path.dirname(os.path.realpath(__file__))
work_dir = "%s/%s" % (work_dir.replace("\\", "/"), 'html')

# Коды команд для выполнения на хабе
DO_NOTHING, RESET_SETTINGS, GET_SETTINGS, EXEC_CODE, RESET_PARAMS = range(5)
CLIENT, PARTNER = 'client', 'partner'

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
# раскомментить, чтобы удалить все таблицы из БД при старте приложения
# db.drop_all()
db.create_all()
# задаем кэширование в зависимости от платформы запуска
from werkzeug.contrib.cache import GAEMemcachedCache, SimpleCache
if 'win' in sys.platform:
    cache = SimpleCache()
else:
    cache = GAEMemcachedCache()

"""
    -----API сервера-----
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
    """Декоратор для проверки аутентификации методов API"""
    @wraps(fn)
    def wrapped(*args, **kwargs):
        access_token = 0
        if request.method == "POST":
            access_token, = validate_post(('access_token',), (str,), (0,))
        elif request.method == "GET":
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


def jsonp(func):
    """Декоратор. Преобразует JSON в JSONP (если передан параметр callback)"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


def validate_user(access_token):
    if not access_token:
        abort(401)
    user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    user = User.query.get_or_404(user_id)
    if not user.user_type:
        abort(400)
    return user


@app.route("/hub/new_device_id", methods=['GET'])
def new_device_id():
    serial_id, = validate_get(('serial_id',), (unicode,), (0,))
    if not serial_id:
        abort(400)
    hub = Hub.query.filter_by(serial_id=serial_id).first()
    if not hub:
        if len(serial_id) == 32:
            hub = Hub(serial_id)
            db.session.add(hub)
        else:
            abort(400)
    new_device_id = str(uuid.uuid4())[-12:]
    hub.device_id = new_device_id
    db.session.commit()
    return jsonify({'success': True, 'device_id': hub.device_id})


@app.route("/hub/device_id", methods=['GET'])
def get_device_id():
    serial_id, = validate_get(('serial_id',), (unicode,), (0,))
    if not serial_id:
        abort(400)
    hub = Hub.query.filter_by(serial_id=serial_id).first()
    if not hub or not hub.device_id:
        return jsonify({'success': False, 'device_id': None})
    return jsonify({'success': True, 'device_id': hub.device_id})


@app.route("/hub/connect", methods=['POST'])
def try_update_post():
    """
    Метод для подключения к хабу. Если идентификатор соответсвтует хабу,
    который нужно обновить, то на хаб отправляется скрипт для запуска
    :return:
    """
    print request.form.items()
    serial_id, = validate_post(('serial_id',), (unicode,), (0,))
    if not serial_id:
        abort(400)
    hub = Hub.query.filter_by(serial_id=serial_id).first()
    if not hub:
        if len(serial_id) == 32:
            hub = Hub(serial_id)
            db.session.add(hub)
        else:
            abort(400)
    utmOn, unsentTicketsCount, totalTicketsCount, retailBufferSize, \
    bufferAge, version, certificateRSA, certificateGOST, utime \
        = validate_post(("utmOn",
                        "unsentTicketsCount",
                        "totalTicketsCount",
                        "retailBufferSize",
                        "bufferAge",
                        "version",
                        "certificateRSABestBefore",
                        "certificateGOSTBestBefore",
                         "utc_time"),
                        (str,) + (int,)*4 + (str,) + (int,)*2 + (str,),
                        (None,) * 9)
    if utmOn.lower().startswith('t'):
        utmOn = True
    else:
        utmOn = False
    hub_st = Hub_statistics.query.filter_by(create_time=utime).first()
    if hub_st:
        hub_st.utm_status = utmOn
        hub_st.unset_tickets_count = unsentTicketsCount
        hub_st.total_tickets_count = totalTicketsCount
        hub_st.retail_buffer_size = retailBufferSize
        hub_st.buffer_age = bufferAge
    else:
        hub.stats.append(Hub_statistics(utmOn, unsentTicketsCount, totalTicketsCount,
                                        retailBufferSize, bufferAge, utime))
    if certificateRSA:
        hub.meta.certificate_rsa_date = datetime.date.today() + datetime.timedelta(days=certificateRSA)
    if certificateGOST:
        hub.meta.certificate_gost_date = datetime.date.today()+ datetime.timedelta(days=certificateGOST)
    if version:
        hub.meta.utm_version = version
    # if (utmOn or unsentTicketsCount or totalTicketsCount
    #         or retailBufferSize or bufferAge):
    #     new_stat = Hub_statistics(utmOn, unsentTicketsCount, totalTicketsCount,
    #                         retailBufferSize, bufferAge)
    #     hub.stats.append(new_stat)
    # if certificateRSA:
    #     hub.hub_meta.certificate_rsa_date = date.fromtimestamp(time.time()
    #                                                            + certificateRSA)
    # if certificateGOST:
    #     hub.hub_meta.certificate_gost_date = date.fromtimestamp(time.time()
    #                                                             + certificateGOST)
    db.session.commit()
    command = DO_NOTHING
    if not hub.sended_settings:
        command = GET_SETTINGS
    if not hub.uploaded_settings:
        command = RESET_SETTINGS
    return jsonify({'success': True, 'command_code': command})


@app.route("/tasks/cleanbd", methods=['POST'])
def cleanbd():
    pass


@app.route("/api/recovery", methods=['POST'])
@jsonp
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
        user = User.query.filter_by(email=email).first_or_404()
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
@jsonp
def api_signup():
    """
    Регистрация пользователя. Требуются почта и два поля пароля.
    Пользователь сохраняется в базе и на его почту высылается ссылка
    для подтверждения адреса почты. Если пользователь не подтвердил
    почту, то он может ещй раз зарегестрироваться.
    :return:
    """
    email, password, conf_password, user_type = validate_post(
        ('email', 'password', 'conf_password', 'type'), (str,) * 4, ('',) * 4)
    if not (email and user_type and password and conf_password == password):
        abort(400)
    token = Token.generate_token(email, app.config['SECRET_KEY'])
    user = User.query.filter_by(email=email, confirmed=False, user_type=user_type).first()
    if not user:
        user = User('', email, Token.generate_token(password, app.config['SECRET_KEY']), user_type)
        if user_type == CLIENT:
            client = Client(user)
            db.session.add(client)
        elif user_type == PARTNER:
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
    # if app.config['DEBUG'] and user.email == 'maxalexdanilchenko@gmail.com':
    #     testdata()
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
@jsonp
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
    user = User.query.filter_by(email=email).first_or_404()
    if Token.confirm_token(user.password, app.config['SECRET_KEY'], None) != password or not user.confirmed:
        abort(401)
    token = Token.generate_token(user.id, app.config['SECRET_KEY'])
    # Получить обратно: user_id = Token.confirm_token(access_token, app.config['SECRET_KEY'], None)
    cache.set(token, user_info(request), app.config['MAX_CACHE_TIME'])
    user.recovery_token = ''
    db.session.commit()
    return jsonify({'success': True, 'access_token': token})


@app.route("/api/newpas", methods=['POST'])
@jsonp
def api_newpas():
    """
    Меняет пароль пользователя, а потом регистрирует его и возвращает access_token
    :return:
    """
    token, password, conf_password = validate_post(('token', 'password', 'conf_password',), (str,) * 3, ('',) * 3)
    if not (token and password and conf_password == password):
        abort(400)
    # email = Token.confirm_token(token, app.config['SECRET_KEY'], None)
    user = User.query.filter_by(recovery_token=token).first_or_404()
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
    поддверждения адреса почты, происходит пометка в БД,
    что пользователь подтвержден, после чего он может войти
    Происходит редирект на страницу успеха
    :param token:
    :return:
    """
    if token:
        email = Token.confirm_token(token, app.config['SECRET_KEY'], app.config['CONFIRM_TIME'])
        # проверить пользователя по почте в базе и пометить, что он подтвердил email
        if not email:
            abort(400)
        user = User.query.filter_by(email=email).first_or_404()
        user.confirmed = True
        db.session.commit()
        return redirect(url_for('success'))


@app.route("/recovery/<string:token>", methods=['GET'])
def recovery(token):
    """
    """
    if token:
        user = User.query.filter_by(recovery_token=token).first_or_404()
        return redirect(url_for('newpassword', email=user.email, token=token))


@app.route("/api/get_user_info", methods=['GET'])
@is_auth
@jsonp
def get_info():
    access_token, = validate_get(('access_token',), (str,), (0,))
    if not access_token:
        abort(400)
    user = validate_user(access_token)
    name = user.name or user.email
    if len(name) > 30:
        name = '%s..' % name[:28]
    return jsonify({'success': True, 'name': name, 'type': user.user_type})


@app.route("/api/get_tree", methods=['GET'])
@is_auth
@jsonp
def api_get_tree():
    access_token, = validate_get(('access_token',), (str,), (0,))
    user = validate_user(access_token)
    if user.user_type == CLIENT:
        tree = get_tree(user.client.group, CLIENT)
        return jsonify({'success': True, 'tree': tree})
    elif user.user_type == PARTNER:
        tree = get_tree(user.partner.group, PARTNER)
        return jsonify({'success': True, 'tree': tree})
    abort(400)


@app.route("/api/connect_hub", methods=['POST'])
@is_auth
@jsonp
def connect_hub():
    access_token, device_id, group_id, name, order_id = validate_post(
        ('access_token', 'device_id', 'group_id', 'name', 'order_id'),
        (str, str, int, unicode, int),
        (0,)*5)
    if not (access_token and device_id and name and group_id):
        abort(400)
    user = validate_user(access_token)
    device = Hub.query.filter_by(device_id=device_id).first_or_404()
    if user.user_type == CLIENT and device.hub_client \
            or user.user_type == PARTNER and device.hub_partner:
        abort(404)
    group = Client_group.query.get_or_404(group_id) if user.user_type == CLIENT \
        else Partner_group.query.get_or_404(group_id)
    if not valid_group_user(group, user):
        abort(404)
    hub = Hub_client(name, device, order_id, group) if user.user_type == CLIENT \
        else Hub_partner(name, device, order_id, group)
    db.session.add(hub)
    db.session.commit()
    return jsonify({'success': True, 'id': hub.id, 'name': name})


@app.route("/api/disconnect_hub", methods=['POST'])
@is_auth
@jsonp
def disconnect_hub():
    access_token, hub_id, group_id = validate_post(
        ('access_token', 'hub_id', 'group_id'),
        (str, int, int),
        (0,)*3)
    if not (access_token and hub_id and group_id):
        abort(400)
    user = validate_user(access_token)
    hub = Hub_client.query.get_or_404(hub_id) if user.user_type == CLIENT \
        else Hub_partner.query.get_or_404(hub_id)
    group = Client_group.query.get_or_404(group_id) if user.user_type == CLIENT \
        else Partner_group.query.get_or_404(group_id)
    if not valid_group_user(group, user):
        abort(404)
    if hub not in group.hubs:
        abort(404)
    db.session.delete(hub)
    db.session.commit()
    return jsonify({'success': True})


@app.route("/api/rename_hub", methods=['POST'])
@is_auth
@jsonp
def rename_hub():
    access_token, hub_id, name = validate_post(
        ('access_token', 'hub_id', 'name'),
        (str, str, unicode),
        (0,)*4)
    if not (access_token and hub_id and name):
        abort(400)
    user = validate_user(access_token)
    hub = Hub_client.query.get_or_404(hub_id) if user.user_type == CLIENT \
        else Hub_partner.query.get_or_404(hub_id)
    group = hub.group
    if not valid_group_user(group, user):
        abort(404)
    hub.name = name
    db.session.commit()
    return jsonify({'success': True, 'name': name})


@app.route("/api/hub_statistics", methods=['GET'])
@is_auth
@jsonp
def hub_statistics():
    access_token, hub_id = validate_get(
        ('access_token', 'hub_id'),
        (str, str),
        (0,)*2)
    if not (access_token and hub_id):
        abort(400)
    user = validate_user(access_token)
    hub = Hub_client.query.get_or_404(hub_id) if user.user_type == CLIENT \
        else Hub_partner.query.get_or_404(hub_id)
    group = hub.group
    if not valid_group_user(group, user):
        abort(404)
    if hub.hub is None:
        abort(404)
    stats = Hub_statistics.query.filter_by(hub_id=hub.hub.id).order_by(desc(Hub_statistics.create_time)).first()
    try:
        data = statistics(hub.hub.meta, stats)
    except Exception as e:
        abort(500)
    return jsonify({'success': True, 'data': data})


@app.route("/api/charts_statistics", methods=['GET'])
@is_auth
@jsonp
def charts_statistics():
    access_token, hub_id, period = validate_get(
        ('access_token', 'hub_id', 'period'),
        (str, str, str),
        (0,)*3)
    if not (access_token and hub_id):
        abort(400)
    user = validate_user(access_token)
    hub = Hub_client.query.get_or_404(hub_id) if user.user_type == CLIENT \
        else Hub_partner.query.get_or_404(hub_id)
    group = hub.group
    if not valid_group_user(group, user):
        abort(404)
    if hub.hub is None:
        abort(404)
    # try:
    if period == 'week':
        q = Hub_statistics.query.filter_by(hub_id=hub.hub.id)\
            .filter(Hub_statistics.create_time > datetime.datetime.utcnow() - datetime.timedelta(days=7))\
            .order_by(asc(Hub_statistics.create_time))\
            .distinct(Hub_statistics.create_time).group_by(func.date(Hub_statistics.create_time))\
            .group_by(func.hour(Hub_statistics.create_time).op('div')(8)*8)
    elif period == 'month':
        q = Hub_statistics.query.filter_by(hub_id=hub.hub.id) \
            .filter(Hub_statistics.create_time > datetime.datetime.utcnow() - datetime.timedelta(days=30)) \
            .order_by(asc(Hub_statistics.create_time)) \
            .distinct(Hub_statistics.create_time).group_by(func.date(Hub_statistics.create_time))
    else:
        q = Hub_statistics.query.filter_by(hub_id=hub.hub.id) \
            .filter(Hub_statistics.create_time > datetime.datetime.utcnow() - datetime.timedelta(days=1)) \
            .order_by(asc(Hub_statistics.create_time)) \
            .distinct(Hub_statistics.create_time).group_by(func.hour(Hub_statistics.create_time))
    # except Exception as e:
    #     abort(500)
    return jsonify({'success': True, 'data': chart_statistics(q.all())})


@app.route("/api/create_group", methods=['POST'])
@is_auth
@jsonp
def create_group():
    access_token, parent_id, name, order_id = validate_post(('access_token', 'parent_id', 'name', 'order_id'),
                                                            (str, int, unicode, int),
                                                            (0,)*4)
    if not (access_token and name and parent_id):
        abort(400)
    user = validate_user(access_token)
    if user.user_type == 'client':
        parent = Client_group.query.get_or_404(parent_id)
        if not valid_group_user(parent, user):
            abort(404)
        new_group = Client_group(name, parent=parent)
        new_group.order_id = order_id
        db.session.add(new_group)
    elif user.user_type == 'partner':
        parent = Partner_group.query.get_or_404(parent_id)
        if not valid_group_user(parent, user):
            abort(404)
        new_group = Partner_group(name, parent=parent)
        new_group.order_id = order_id
        db.session.add(new_group)
    else:
        abort(400)
    db.session.commit()
    return jsonify({'success': True, 'id': new_group.id, 'name': name})


@app.route("/api/remove_group", methods=['POST'])
@is_auth
@jsonp
def remove_group():
    access_token, group_id = validate_post(('access_token', 'group_id'), (str, int), (0,)*2)
    if not (access_token and group_id):
        abort(400)
    user = validate_user(access_token)
    if user.user_type == 'client':
        group = Client_group.query.get_or_404(group_id)
        if not valid_group_user(group, user):
            abort(404)
        db.session.delete(group)
    elif user.user_type == 'partner':
        group = Partner_group.query.get_or_404(group_id)
        if not valid_group_user(group, user):
            abort(404)
        db.session.delete(group)
    else:
        abort(400)
    db.session.commit()
    return jsonify({'success': True})


@app.route("/api/rename_group", methods=['POST'])
@is_auth
@jsonp
def rename_group():
    access_token, group_id, name = validate_post(('access_token', 'group_id', 'name'), (str, int, unicode), (0,)*3)
    if not (access_token and name and group_id):
        abort(400)
    user = validate_user(access_token)
    if user.user_type == 'client':
        group = Client_group.query.get_or_404(group_id)
        if not valid_group_user(group, user):
            abort(404)
        group.name = name
    elif user.user_type == 'partner':
        group = Partner_group.query.get_or_404(group_id)
        if not valid_group_user(group, user):
            abort(404)
        group.name = name
    else:
        abort(400)
    db.session.commit()
    return jsonify({'success': True, 'name': name})


@app.route("/api/reorder", methods=['POST'])
@is_auth
@jsonp
def reorder():
    access_token, parent_id = validate_post(('access_token', 'parent_id'), (str, int), (0,)*2)
    if not (access_token and parent_id):
        abort(400)
    children = parseList('children')
    if not children:
        abort(400)
    user = validate_user(access_token)
    if user.user_type == CLIENT:
        if not valid_group_user(Client_group.query.get_or_404(parent_id), user):
            abort(401)
        for key in children:
            if children[key]['type'] == 'hub':
                hub = Hub_client.query.get_or_404(int(children[key]['id']))
                if not valid_group_user(hub.group, user):
                    abort(401)
                hub.order_id = int(children[key]['order_id'])
                hub.group_id = parent_id
                db.session.commit()
            if children[key]['type'] == 'tab':
                group = Client_group.query.get_or_404(int(children[key]['id']))
                if not valid_group_user(group, user):
                    abort(401)
                group.order_id = int(children[key]['order_id'])
                group.parent_id = parent_id
                db.session.commit()
    elif user.user_type == PARTNER:
        if not valid_group_user(Partner_group.query.get_or_404(parent_id), user):
            abort(401)
        for key in children:
            if children[key]['type'] == 'hub':
                hub = Hub_partner.query.get_or_404(int(children[key]['id']))
                if not valid_group_user(hub.group, user):
                    abort(401)
                hub.order_id = int(children[key]['order_id'])
                hub.group_id = parent_id
                db.session.commit()
            if children[key]['type'] == 'tab':
                group = Partner_group.query.get_or_404(int(children[key]['id']))
                if not valid_group_user(group, user):
                    abort(401)
                group.order_id = int(children[key]['order_id'])
                group.parent_id = parent_id
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
    if Hub.query.filter_by(device_id='hub1').first():
        return
    user = User.query.filter_by(email='maxalexdanilchenko@gmail.com', user_type='partner').first()

    new_group = user.partner.group


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
    hub1.order_partner_id = 2
    hub2.order_partner_id = 1
    new_sub_group.hubs.extend([hub3, hub4])
    hub3.order_partner_id = 0
    hub4.order_partner_id = 1
    new_sub_sub_group.hubs.extend([hub5])
    db.session.commit()

    tree = get_tree(new_group, 'partner')
    print tree

env_serv = os.getenv('SERVER_SOFTWARE')


if app.config['DEBUG']:
    base = ''.join(str(0) for i in range(32))
    if not Hub.query.filter_by(serial_id=base).first():
        db.session.add_all(
            [Hub(base[:32-len(str(i))]+str(i), device_id='device-id-%d' % i)
             for i in range(app.config['TEST_HUB_NUM'])])
        db.session.commit()


if not (env_serv and env_serv.startswith('Google App Engine/')):
    if 'win' in sys.platform and __name__ == "__main__":
        app.run(host='0.0.0.0', port=81)
