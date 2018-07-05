import logging

import click

from flask.cli import FlaskGroup
from yawc.db.query.user import (
    create_user, delete_user, list_users, set_user_password,
    verify_credentials)

from .app import create_app, setup_logging

logger = logging.getLogger(__name__)


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    pass


@cli.command(name='run')
@click.option('--host', '-h', default='127.0.0.1')
@click.option('--port', '-p', type=int, default=5000)
def cmd_run(host, port):
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    setup_logging()

    app = create_app()
    server = pywsgi.WSGIServer(
        (host, port), app, handler_class=WebSocketHandler, log=logger)
    server.serve_forever()


@cli.group(name='user')
def grp_user():
    """User management"""
    pass


@grp_user.command(name='create')
@click.argument('email')
@click.option('--name', prompt=True)
@click.option(
    '--password', prompt=True, hide_input=True,
    confirmation_prompt=True)
def cmd_user_create(email, name, password):
    user_id = create_user(name=name, email=email, password=password)
    print('Created user: {}'.format(user_id))


@grp_user.command(name='list')
def cmd_user_list():
    for row in list_users():
        print('{} {}'.format(row.id, row.username))


@grp_user.command(name='set-password')
@click.argument('user_id', type=int)
@click.option(
    '--password', prompt=True, hide_input=True,
    confirmation_prompt=True)
def cmd_user_set_password(user_id, password):
    set_user_password(user_id, password)


@grp_user.command(name='delete')
@click.argument('user_id', type=int)
def cmd_user_delete(user_id):
    delete_user(user_id)


@grp_user.command(name='check-password')
@click.argument('username')
@click.option(
    '--password', prompt=True, hide_input=True,
    confirmation_prompt=False)
def cmd_user_check_password(username, password):
    result = verify_credentials(username, password)
    if result:
        print('Valid')
    else:
        print('Wrong username or password')
