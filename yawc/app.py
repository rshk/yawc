import logging
import sys

from flask import Flask, redirect
from flask_cors import CORS
from flask_sockets import Sockets
from gevent import monkey
from graphql_ws.gevent import GeventSubscriptionServer

from .auth import load_auth_info
from .graphqlview import GraphQLView
from .schema import schema

monkey.patch_all()


logger = logging.getLogger(__name__)


def create_app():

    app = Flask(__name__)

    @app.route('/')
    def index():
        return redirect('/graphql')

    # GraphQL endpoints ----------------------------------------------

    app.add_url_rule(
        '/graphql',
        view_func=load_auth_info(GraphQLView.as_view(
            'graphql', schema=schema, graphiql=True)))

    # Optional, for adding batch query support (used in Apollo-Client)
    app.add_url_rule(
        '/graphql/batch',
        view_func=load_auth_info(GraphQLView.as_view(
            'graphql-batch', schema=schema, batch=True)))

    # RESTful methods for authentication -----------------------------
    # TODO: provide this via GraphQL API

    # @app.errorhandler(401)
    # def handle_401(error):
    #     return Response(str(error), 401, {
    #         'WWWAuthenticate': 'Basic realm="Login Required"',
    #     })

    # @app.route('/auth', methods=['POST'])
    # def authenticate_user():
    #     username = request.form['username']
    #     password = request.form['password']
    #     user = verify_credentials(username, password)

    #     if user:
    #         token = _create_user_jwt(user)
    #         return json.dumps({'token': token.decode()}), 200, {
    #             'Content-type': 'text/json'}

    #     raise Unauthorized('Bad username / password')

    # Websockets -----------------------------------------------------

    sockets = Sockets(app)
    app.app_protocol = lambda environ_path_info: 'graphql-ws'
    subscription_server = GeventSubscriptionServer(schema)

    @sockets.route('/subscriptions')
    def echo_socket(ws):
        subscription_server.handle(ws)
        return []

    # Add CORS support -----------------------------------------------

    CORS(app)

    return app


def setup_logging():
    from nicelog.formatters import Colorful
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(Colorful(
        show_date=True,
        show_function=True,
        show_filename=True,
        message_inline=False))
    handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)
    logger.debug('Debugging logger enabled')

    # DEBUG log is way too verbose on this one
    (logging
     .getLogger('Rx')
     .setLevel(logging.INFO))
