# -*- coding: utf-8 -*-
# Вспомогательные скрипты для функций REST-API
import re
from flask import request


def validate_get(names, types, defaults):
    if not len(names) == len(types) == len(defaults):
        raise AppException("different length of tuples")
    try:
        return (types[i](request.args.get(names[i])) if request.args.get(names[i]) else defaults[i]
                for i in range(len(names)))
    except:
        return False


def validate_post(names, types, defaults):
    if not len(names) == len(types) == len(defaults):
        raise AppException("different length of tuples")
    try:
        return (types[i](request.form[names[i]]) if names[i] in request.form else defaults[i]
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
        return None if re.findall('[^0-9\.]', text) else int(re.search('[0-9]+', text).group())
    elif isinstance(text, (int, long, float)):
        return int(text)
    else:
        return text


def user_info(req=request):
    return req.user_agent.browser+req.user_agent.platform+req.remote_addr


def make_code_for_id(hub_id):
    return "code"


def get_tree(node, user_type):
    if user_type not in ('partner', 'client'):
        return None
    groups_list = [get_tree(child, user_type) for child in node.childes]
    hubs_list = [{"id": hub.id,
                  "type": "hub",
                  "name": hub.partner_name if user_type == 'partner' else hub.client_name,
                  "order_id": hub.order_partner_id if user_type == 'partner' else hub.order_client_id} for hub in node.hubs]
    return dict({"id": node.id,
                 "type": "group",
                 "name": node.name,
                 "order_id": node.order_id,
                 "children": groups_list + hubs_list})


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
