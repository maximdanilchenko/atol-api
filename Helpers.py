# -*- coding: utf-8 -*-
# Вспомогательные скрипты для функций REST-API
import re
from flask import request
import datetime

red_border, yellow_border, day_border = 3600 * 36, 3600 * 24, 60  # константы
default_color = 'dark-grey'

def validate_get(names, types, defaults):
    if not len(names) == len(types) == len(defaults):
        raise AppException("different length of tuples")
    try:
        return (
        types[i](request.args.get(names[i])) if request.args.get(names[i]) else
        defaults[i]
        for i in range(len(names)))
    except:
        return False


def validate_post(names, types, defaults):
    if not len(names) == len(types) == len(defaults):
        raise AppException("different length of tuples")
    try:
        return (
        types[i](request.form[names[i]]) if names[i] in request.form else
        defaults[i]
        for i in range(len(names)))
    except:
        return False


class AppException(Exception):
    pass


def to_int(text):
    """
    Проверяет число в текстовом формате и возвращает корректное значение типа int
    @param text: число в текстовом формате
    @return: корректное значение типа int
    """
    if not text:
        return None
    if isinstance(text, basestring):
        return None if re.findall('[^0-9\.]', text) else int(
            re.search('[0-9]+', text).group())
    elif isinstance(text, (int, long, float)):
        return int(text)
    else:
        return text


def user_info(req=request):
    return req.user_agent.browser + req.user_agent.platform + req.remote_addr


def make_code_for_id(hub_id):
    return "code"


def get_tree(node, user_type):
    if user_type not in ('partner', 'client'):
        return None
    groups_list = [get_tree(child, user_type) for child in node.childes]
    hubs_list = [{"id": hub.id,
                  "type": "hub",
                  "name": hub.name,
                  "order_id": hub.order_id}
                 for hub in node.hubs]
    return {"id": node.id,
            "type": "group",
            "name": node.name,
            "order_id": node.order_id,
            "hub_num": len(hubs_list),
            "group_num": len(groups_list),
            "children": groups_list + hubs_list}


def statistics(meta, stats):
    info = {}
    limit = datetime.date.today() + datetime.timedelta(days=60)
    info['utm_version'] = [meta.utm_version, default_color] if meta.utm_version is not None else ['-', default_color]

    if meta.certificate_rsa_date is not None:
        d = (meta.certificate_rsa_date - datetime.date.today()).days
        rsa_color = 'red' if meta.certificate_rsa_date < limit else 'green'
        info['certificate_rsa_date'] = [d, rsa_color]
    else:
        info['certificate_rsa_date'] = ['-', default_color]

    if meta.certificate_gost_date is not None:
        d = (meta.certificate_gost_date - datetime.date.today()).days
        gost_color = 'red' if meta.certificate_gost_date < limit else 'green'
        info['certificate_gost_date'] = [d, gost_color]
    else:
        info['certificate_gost_date'] = ['-', default_color]

    if stats.utm_status is not None:
        t = u'Включен' if stats.utm_status else u'Выключен'
        z = 1 if stats.utm_status else 0
        utm_color = 'green' if stats.utm_status else default_color
        info['utm_status'] = [t, utm_color, z]
    else:
        info['utm_status'] = ['-', default_color, None]

    info['unset_tickets_count'] = [stats.unset_tickets_count, default_color] if stats.unset_tickets_count is not None else ['-', default_color]
    info['total_tickets_count'] = [stats.total_tickets_count, default_color] if stats.total_tickets_count is not None else ['-', default_color]
    info['retail_buffer_size'] = [stats.retail_buffer_size, default_color] if stats.retail_buffer_size is not None else ['-', default_color]

    if stats.buffer_age is not None:
        buffer_color = 'green' if stats.buffer_age < yellow_border else \
            'yellow' if stats.buffer_age < red_border else 'red'
        t = stats.buffer_age
        info['buffer_age'] = [u"%s д, %s ч, %s м" % (
            t // 86400, t % 86400 // 3600, t % 3600 // 60), buffer_color]
    else:
        info['buffer_age'] = ['-', default_color]

    info['time'] = stats.create_time.strftime("%Y-%m-%d %H:%M:%S+00:00")
    return info


def chart_statistics(stats):
    total_tickets_count_chart = {'times': [], 'values': []}
    unset_tickets_checks_count_chart = {'times': [], 'tickets': [], 'checks': []}
    utm_status_chart = {'times': [], 'values': []}

    for n in range(len(stats)):
        total_tickets_count_chart['values'].append(stats[n].total_tickets_count)
        total_tickets_count_chart['times'].append(stats[n].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
        unset_tickets_checks_count_chart['checks'].append(stats[n].retail_buffer_size)
        unset_tickets_checks_count_chart['tickets'].append(stats[n].unset_tickets_count)
        unset_tickets_checks_count_chart['times'].append(stats[n].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
        utm_status_chart['values'].append(stats[n].utm_status)
        utm_status_chart['times'].append(stats[n].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))

    # for n, stat in enumerate(stats[1:-1]):
    #     if not (stats[n - 1].total_tickets_count == stats[n].total_tickets_count == stats[n + 1].total_tickets_count):
    #         total_tickets_count_chart['values'].append(stats[n].total_tickets_count)
    #         total_tickets_count_chart['times'].append(stats[n].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
    #     if not (stats[n - 1].unset_tickets_count == stats[n].unset_tickets_count == stats[n + 1].unset_tickets_count) or \
    #             not (stats[n - 1].retail_buffer_size == stats[n].retail_buffer_size == stats[n + 1].retail_buffer_size):
    #         unset_tickets_checks_count_chart['checks'].append(stats[n].retail_buffer_size)
    #         unset_tickets_checks_count_chart['tickets'].append(stats[n].unset_tickets_count)
    #         unset_tickets_checks_count_chart['times'].append(stats[n].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
    #     if not (stats[n - 1].utm_status == stats[n].utm_status == stats[n + 1].utm_status):
    #         utm_status_chart['values'].append(stats[n].utm_status)
    #         utm_status_chart['times'].append(stats[n].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
    #
    # total_tickets_count_chart['values'].append(stats[-1].total_tickets_count)
    # total_tickets_count_chart['times'].append(stats[-1].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
    # unset_tickets_checks_count_chart['checks'].append(stats[-1].retail_buffer_size)
    # unset_tickets_checks_count_chart['tickets'].append(stats[-1].unset_tickets_count)
    # unset_tickets_checks_count_chart['times'].append(stats[-1].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))
    # utm_status_chart['values'].append(stats[-1].utm_status)
    # utm_status_chart['times'].append(stats[-1].create_time.strftime("%Y-%m-%d %H:%M:%S+00:00"))

    return {
        "total_tickets_count": total_tickets_count_chart,
        "unset_tickets_checks_count": unset_tickets_checks_count_chart,
        "utm_status": utm_status_chart,
    }

# --проверка на пренадлежность группы пользователю
def valid_group_user(group, user):
    if user.user_type == 'client':
        gr = group
        user_gr = gr.client
        while not user_gr:
            gr = gr.parent
            user_gr = gr.client
        if user_gr.user != user:
            return False
    elif user.user_type == 'partner':
        gr = group
        user_gr = gr.partner
        while not user_gr:
            gr = gr.parent
            user_gr = gr.partner
        if user_gr.user != user:
            return False
    return True


def parseList(name):
    result = {}
    p = re.compile('%s\[(?P<i>\d+)\]\[(?P<type>\w+)\]' % name)
    for key in request.form.iterkeys():
        m = re.match(p, key)
        if m:
            d = m.groupdict()
            if not result.has_key(d['i']):
                result[d['i']] = {}
            result[d['i']][d['type']] = request.form[key]
    return result


def get_settings(settings):
    st = settings
    return {
        "supervisor": {
            "max_timer_transport_restart": st.supervisor.max_timer_transport_restart,
            "restart_if_no_cert": st.supervisor.restart_if_no_cert,
            "logging": st.supervisor.logging,
            "max_force_restart_count": st.supervisor.max_force_restart_count,
            "max_timer_transport_reboot": st.supervisor.max_timer_transport_reboot,
            "restart_allow_reboot": st.supervisor.restart_allow_reboot,
            "scan_period": st.supervisor.scan_period,
            "max_timer_transport_force_restart": st.supervisor.max_timer_transport_force_restart,
            "supervisor_enabled": st.supervisor.supervisor_enabled
        },
        "scanner": {
            "sens": st.scanner.sens,
            "port": st.scanner.port,
            "suffix": st.scanner.suffix
        },
        "proxy": {
            "proxy_port": st.proxy.proxy_port,
            "proxy_type": st.proxy.proxy_type
        },
        "mail": {
            "mail": st.mail.mail
        },
        "vpn": {
            "tls": st.vpn.tls,
            "zip": st.vpn.zip,
            "vpn_type": st.vpn.vpn_type,
            "proto": st.vpn.proto,
            "cipher": st.vpn.cipher,
            "hosts": st.vpn.hosts,
            "interface": st.vpn.interface
        },
        "transport": {
            "access_control_allow_origin": st.transport.access_control_allow_origin,
            "key_pincode": st.transport.key_pincode,
            "user_pincode": st.transport.user_pincode,
            "rolling_log": st.transport.rolling_log
        },
        "hostapd": {
            "ap_name": st.hostapd.ap_name,
            "ap_channel": st.hostapd.ap_channel,
            "ap_pass": st.hostapd.ap_pass
        },
        "wifi": {
            "network": st.wifi.network,
            "ap_pass": st.wifi.ap_pass,
            "ip": st.wifi.ip,
            "mask": st.wifi.mask,
            "ap_channel": st.wifi.ap_channel,
            "ap_list": st.wifi.ap_list,
            "broadcast": st.wifi.broadcast,
            "ap_name": st.wifi.ap_name,
            "mode": st.wifi.mode,
            "dns": st.wifi.dns,
            "address_type": st.wifi.address_type,
            "gateway": st.wifi.gateway
        },
        "internet": {
            "gateway": st.internet.gateway
        },
        "ethernet": {
            "network": st.ethernet.network,
            "ip": st.ethernet.ip,
            "mask": st.ethernet.mask,
            "broadcast": st.ethernet.broadcast,
            "dns": st.ethernet.dns,
            "address_type": st.ethernet.address_type,
            "gateway": st.ethernet.gateway
        },
        "modem": {
            "modem_phone": st.modem.modem_phone,
            "modem_password": st.modem.modem_password,
            "modem_user": st.modem.modem_user,
            "modem_apn": st.modem.modem_apn
        },
        "ttn": {
            "logging": st.ttn.logging,
            "auth": st.ttn.auth
        }
    }


def set_settings(settings, json):
    st = settings

    st.supervisor.max_timer_transport_restart, = json["supervisor"]["max_timer_transport_restart"]
    st.supervisor.restart_if_no_cert, = json["supervisor"]["restart_if_no_cert"]
    st.supervisor.logging, = json["supervisor"]["logging"]
    st.supervisor.max_force_restart_count, = json["supervisor"]["max_force_restart_count"]
    st.supervisor.max_timer_transport_reboot, = json["supervisor"]["max_timer_transport_reboot"]
    st.supervisor.restart_allow_reboot, = json["supervisor"]["restart_allow_reboot"]
    st.supervisor.scan_period, = json["supervisor"]["scan_period"]
    st.supervisor.max_timer_transport_force_restart, = json["supervisor"]["max_timer_transport_force_restart"]
    st.supervisor.supervisor_enabled = json["supervisor"]["supervisor_enabled"]

    st.scanner.sens, = json["scanner"]["sens"]
    st.scanner.port, = json["scanner"]["port"]
    st.scanner.suffix = json["scanner"]["suffix"]

    st.proxy.proxy_port, = json["proxy"]["proxy_port"]
    st.proxy.proxy_type = json["proxy"]["proxy_type"]

    st.mail.mail = json["mail"]["mail"]

    st.vpn.tls, = json["vpn"]["tls"]
    st.vpn.zip, = json["vpn"]["zip"]
    st.vpn.vpn_type, = json["vpn"]["vpn_type"]
    st.vpn.proto, = json["vpn"]["proto"]
    st.vpn.cipher, = json["vpn"]["cipher"]
    st.vpn.hosts, = json["vpn"]["hosts"]
    st.vpn.interface = json["vpn"]["interface"]

    st.transport.access_control_allow_origin, = json["transport"]["access_control_allow_origin"]
    st.transport.key_pincode, = json["transport"]["key_pincode"]
    st.transport.user_pincode, = json["transport"]["user_pincode"]
    st.transport.rolling_log = json["transport"]["rolling_log"]

    st.hostapd.ap_name, = json["hostapd"]["ap_name"]
    st.hostapd.ap_channel, = json["hostapd"]["ap_channel"]
    st.hostapd.ap_pass = json["hostapd"]["ap_pass"]

    st.wifi.network, = json["wifi"]["network"]
    st.wifi.ap_pass, = json["wifi"]["ap_pass"]
    st.wifi.ip, = json["wifi"]["ip"]
    st.wifi.mask, = json["wifi"]["mask"]
    st.wifi.ap_channel, = json["wifi"]["ap_channel"]
    st.wifi.ap_list, = json["wifi"]["ap_list"]
    st.wifi.broadcast, = json["wifi"]["broadcast"]
    st.wifi.ap_name, = json["wifi"]["ap_name"]
    st.wifi.mode, = json["wifi"]["mode"]
    st.wifi.dns, = json["wifi"]["dns"]
    st.wifi.address_type, = json["wifi"]["address_type"]
    st.wifi.gateway = json["wifi"]["gateway"]

    st.internet.gateway = json["internet"]["gateway"]

    st.ethernet.network, = json["ethernet"]["network"]
    st.ethernet.ip, = json["ethernet"]["ip"]
    st.ethernet.mask, = json["ethernet"]["mask"]
    st.ethernet.broadcast, = json["ethernet"]["broadcast"]
    st.ethernet.dns, = json["ethernet"]["dns"]
    st.ethernet.address_type, = json["ethernet"]["address_type"]
    st.ethernet.gateway = json["ethernet"]["gateway"]

    st.modem.modem_phone, = json["modem"]["modem_phone"]
    st.modem.modem_password, = json["modem"]["modem_password"]
    st.modem.modem_user, = json["modem"]["modem_user"]
    st.modem.modem_apn = json["modem"]["modem_apn"]

    st.ttn.logging, = json["ttn"]["logging"]
    st.ttn.auth = json["ttn"]["auth"]

