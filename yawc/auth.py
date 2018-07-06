import base64
import functools
import logging
import os
from collections import namedtuple

import jwt
from flask import request
from jwt.exceptions import InvalidTokenError
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Unauthorized as _Unauthorized
from yawc.db.query.user import get_user, get_user_by_email, verify_credentials

logger = logging.getLogger(__name__)

AuthInfo = namedtuple('AuthInfo', 'user')

WSRequestContext = namedtuple('WSRequestContext', 'auth_info')


class Unauthorized(_Unauthorized):
    """Sub-class of Unauthorized, setting WWW-Authenticate header properly
    """

    def get_headers(self, environ=None):
        return super().get_headers(environ) + [(
            'WWW-Authenticate', 'Basic realm="Login Required"',
        )]


def load_auth_info(fn):
    """View decorator, adding authorization information to the request"""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        authz = request.headers.get('Authorization')
        user_info = _parse_authorization_header(authz)

        # request is passed as "context" to GraphQL functions
        request.auth_info = AuthInfo(user=user_info)

        # if user_info is None:
        #     raise Unauthorized('Authentication required')

        return fn(*args, **kwargs)
    return wrapper


def _parse_authorization_header(value):
    if not value:
        return None
    try:
        atype, avalue = value.split(' ', 1)
    except ValueError:
        raise BadRequest('Malformed Authorization header')

    token_type = atype.lower()

    if token_type == 'basic':
        username, password = _parse_basic_auth(avalue)
        user = verify_credentials(username, password)
        if not user:
            raise Unauthorized('Bad username / password')
        return user

    if token_type == 'bearer':
        return _get_user_from_jwt(avalue)

    raise BadRequest('Unsupported authorization type')


def _parse_basic_auth(value):
    try:
        _decoded = base64.decodestring(value.encode()).decode()
        username, password = _decoded.split(':', 1)
    except ValueError:
        raise BadRequest('Invalid basic authorization')
    return username, password


def _get_user_from_jwt(avalue):
    try:
        jwt_data = _verify_user_jwt(avalue)

    except InvalidTokenError:
        raise Unauthorized('Bad JWT token')

    else:
        user = get_user(jwt_data['id'])
        if user is None:
            raise Unauthorized('Bad JWT token')
        return user


JWT_SECRET_KEY = os.environ['SECRET_KEY']


def _create_user_jwt(user):
    return jwt.encode({'id': user.id}, JWT_SECRET_KEY, algorithm='HS256')


def _verify_user_jwt(token):
    return jwt.decode(token.encode(), JWT_SECRET_KEY, algorithms=['HS256'])


def get_token_for_credentials(email, password):  # -> token
    if verify_credentials(email, password):
        user = get_user_by_email(email)
        return _create_user_jwt(user)
    return None


def get_socket_context(payload):
    logger.debug('Get socket context %s', repr(payload))

    token = payload.get('authToken')
    user = None
    if token:
        user = _get_user_from_jwt(token)

    return WSRequestContext(auth_info=AuthInfo(user=user))
