from json import dumps
from urllib.parse import urlparse, urljoin
from flask import request


def users_to_json(users):
    json_data = []
    for user in users:
        user_data = {}
        for k, v in user.__dict__.items():
            user_data[str(k)] = v
        json_data.append(user_data)

    return dumps(json_data)
