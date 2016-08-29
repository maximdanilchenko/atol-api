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
    children = node.childes
    children_dict = [get_tree(child, user_type) for child in children if children]
    return dict({"id": node.id,
             "name": node.name,
             "hubs": [{"id": hub.id,
                       "name": hub.partner_name if user_type == 'partner' else hub.client_name} for hub in node.hubs],
             "children": children_dict})
