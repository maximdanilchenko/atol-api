# -*- coding: utf-8 -*-
# Генерация/подтверждение токена
from itsdangerous import URLSafeTimedSerializer as urlsave


def generate_token(target, secret_key):
    serializer = urlsave(secret_key)
    return serializer.dumps(target)


def confirm_token(token, secret_key, expiration):
    serializer = urlsave(secret_key)
    try:
        target = serializer.loads(
            token,
            max_age=expiration
        )
    except:
        return False
    return target
