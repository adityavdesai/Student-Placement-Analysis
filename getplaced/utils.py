from json import dumps
from urllib.parse import urlparse, urljoin

from flask import request
from flask_pymongo import DESCENDING


def users_to_json(users):
    json_data = []
    for user in users:
        user_data = {}
        for k, v in user.__dict__.items():
            user_data[str(k)] = v
        json_data.append(user_data)

    return dumps(json_data)


def get_current_id(table):
    """Function to return the latest ID based on the database entries"""
    _id = table.find().sort("_id", DESCENDING).limit(1)[0]['_id']
    return int(_id) + 1


def is_safe_url(target: str) -> bool:
    """Returns whether or not the target URL is safe or a malicious redirect"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
