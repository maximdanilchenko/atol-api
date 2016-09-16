# -*- coding: utf-8 -*-
# Определение архитектуры базы данных
from datetime import datetime
from App import db
from Helpers import AppException
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    recovery_token = db.Column(db.String(128))
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False,
                        unique=True)

    group = db.relationship('Client_group', backref='client', uselist=False)

    def __init__(self, user):
        self.user = user
        self.group = Client_group(user.name if user.name else user.email)


class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False,
                        unique=True)

    group = db.relationship('Partner_group', backref='partner', uselist=False)

    def __init__(self, user):
        self.user = user
        self.group = Partner_group(user.name if user.name else user.email)


class Client_group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    parent_id = db.Column(db.Integer, db.ForeignKey(id))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), unique=True)
    order_id = db.Column(db.Integer)

    childes = db.relationship('Client_group', cascade="all, delete",
                              backref=db.backref('parent', remote_side=id),
                              lazy='dynamic')
    hubs = db.relationship('Hub_client', cascade="all, delete", backref='group',
                           lazy='dynamic')

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent


class Partner_group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    parent_id = db.Column(db.Integer, db.ForeignKey(id))
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'), unique=True)
    order_id = db.Column(db.Integer)

    childes = db.relationship('Partner_group', cascade="all, delete",
                              backref=db.backref('parent', remote_side=id),
                              lazy='dynamic')
    hubs = db.relationship('Hub_partner', cascade="all, delete", backref='group',
                           lazy='dynamic')

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent


class Hub_partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    group_id = db.Column(db.Integer, db.ForeignKey('partner_group.id'),
                         nullable=False)
    order_id = db.Column(db.Integer)
    device_id = db.Column(db.String(128), db.ForeignKey('hub.device_id', onupdate="set null"))

    def __init__(self, name, hub, order_id=0, group=None):
        self.name = name
        self.hub = hub
        self.order_id = order_id
        self.group = group


class Hub_client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    group_id = db.Column(db.Integer, db.ForeignKey('client_group.id'),
                         nullable=False)
    order_id = db.Column(db.Integer)
    device_id = db.Column(db.String(128), db.ForeignKey('hub.device_id', onupdate="cascade"))

    def __init__(self, name, hub, order_id=0, group=None):
        self.name = name
        self.hub = hub
        self.order_id = order_id
        self.group = group


class Hub(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    serial_id = db.Column(db.String(32), unique=True, nullable=False)
    device_id = db.Column(db.String(128), unique=True)

    uploaded_settings = db.Column(db.Boolean, default=True)
    sended_settings = db.Column(db.Boolean, default=True)

    hub_client = db.relationship('Hub_client', backref='hub', uselist=False)
    hub_partner = db.relationship('Hub_partner', backref='hub', uselist=False)

    meta = db.relationship('Hub_meta', backref='hub', uselist=False)
    settings = db.relationship('Hub_settings', backref='hub', uselist=False)
    stats = db.relationship('Hub_statistics', backref='hub', lazy='dynamic')

    def __init__(self, serial_id, device_id=None):
        self.meta = Hub_meta()
        self.settings = Hub_settings()
        self.serial_id = serial_id
        if device_id:
            self.device_id = device_id


class Hub_meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hub_id = db.Column(db.Integer, db.ForeignKey('hub.id'), unique=True)
    utm_version = db.Column(db.String(96))
    certificate_rsa_date = db.Column(db.Date)
    certificate_gost_date = db.Column(db.Date)


class Hub_statistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utm_status = db.Column(db.Boolean, default=False)
    unset_tickets_count = db.Column(db.Integer)
    total_tickets_count = db.Column(db.Integer)
    retail_buffer_size = db.Column(db.Integer)
    buffer_age = db.Column(db.BigInteger)

    create_time = db.Column(db.DateTime)

    hub_id = db.Column(db.Integer, db.ForeignKey('hub.id'))

    def __init__(self, utm_status, unset_tickets_count, total_tickets_count,
                 retail_buffer_size, buffer_age):
        self.utm_status = utm_status
        self.unset_tickets_count = unset_tickets_count
        self.total_tickets_count = total_tickets_count
        self.retail_buffer_size = retail_buffer_size
        self.buffer_age = buffer_age

        self.create_time = datetime.utcnow()


# Здоровеееенная (но простая) часть БД, отвечающая за хранение настроек - - - -
class Hub_settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    supervisor = db.relationship('Supervisor', backref='hub_settings', uselist=False)
    scanner = db.relationship('Scanner', backref='hub_settings', uselist=False)
    proxy = db.relationship('Proxy', backref='hub_settings', uselist=False)
    mail = db.relationship('Mail', backref='hub_settings', uselist=False)
    vpn = db.relationship('Vpn', backref='hub_settings', uselist=False)
    transport = db.relationship('Transport', backref='hub_settings', uselist=False)
    hostapd = db.relationship('Hostapd', backref='hub_settings', uselist=False)
    wifi = db.relationship('Wifi', backref='hub_settings', uselist=False)
    internet = db.relationship('Internet', backref='hub_settings', uselist=False)
    ethernet = db.relationship('Ethernet', backref='hub_settings',uselist=False)
    modem = db.relationship('Modem', backref='hub_settings', uselist=False)
    ttn = db.relationship('Ttn', backref='hub_settings', uselist=False)

    hub_id = db.Column(db.Integer, db.ForeignKey('hub.id'), unique=True)


class Supervisor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    max_timer_transport_restart = db.Column(db.Integer)
    restart_if_no_cert = db.Column(db.Boolean)
    logging = db.Column(db.Enum('release', 'debug'))
    max_force_restart_count = db.Column(db.Integer)
    max_timer_transport_reboot = db.Column(db.Integer)
    restart_allow_reboot = db.Column(db.Boolean)
    scan_period = db.Column(db.Integer)
    max_timer_transport_force_restart = db.Column(db.Integer)
    supervisor_enabled = db.Column(db.Boolean)

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Scanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sens = db.Column(db.Integer)
    port = db.Column(db.String(128))
    suffix = db.Column(db.String(64))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Proxy(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    proxy_port = db.Column(db.Integer)
    proxy_type = db.Column(db.String(128))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    mail = db.Column(db.String(128))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Vpn(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tls = db.Column(db.Enum('enable', 'disable'))
    zip = db.Column(db.Enum('enable', 'disable'))
    vpn_type = db.Column(db.Enum('client', 'off'))
    proto = db.Column(db.String(32))
    cipher = db.Column(db.String(32))
    hosts = db.Column(db.String(128))
    interface = db.Column(db.String(128))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Transport(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    access_control_allow_origin = db.Column(db.String(128))
    key_pincode = db.Column(db.String(128))
    user_pincode = db.Column(db.String(128))
    rolling_log = db.Column(db.Enum('off', 'on'))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Hostapd(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    ap_name = db.Column(db.String(128))
    ap_channel = db.Column(db.String(32))
    ap_pass = db.Column(db.String(128))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Wifi(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    network = db.Column(db.String(64))
    ap_pass = db.Column(db.String(64))
    ip = db.Column(db.String(64))
    mask = db.Column(db.String(64))
    ap_channel = db.Column(db.String(64))
    ap_list = db.Column(db.String(64))
    broadcast = db.Column(db.String(64))
    ap_name = db.Column(db.String(128))
    mode = db.Column(db.String(64))
    dns = db.Column(db.String(64))
    address_type = db.Column(db.String(64))
    gateway = db.Column(db.String(64))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Internet(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    gateway = db.Column(db.String(64))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Ethernet(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    network = db.Column(db.String(64))
    ip = db.Column(db.String(64))
    mask = db.Column(db.String(64))
    broadcast = db.Column(db.String(64))
    dns = db.Column(db.String(64))
    address_type = db.Column(db.String(64))
    gateway = db.Column(db.String(64))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Modem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    modem_phone = db.Column(db.String(32))
    modem_password = db.Column(db.String(64))
    modem_user = db.Column(db.String(64))
    modem_apn = db.Column(db.String(64))

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)


class Ttn(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    logging = db.Column(db.Enum('release', 'debug'))
    auth = db.Column(db.Boolean)

    settings_id = db.Column(db.Integer, db.ForeignKey('hub_settings.id'),
                            unique=True)
