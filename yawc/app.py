import logging
import sys

from flask import Flask, redirect
from flask_cors import CORS
from flask_sockets import Sockets
from gevent import monkey
from graphql_ws.gevent import GeventSubscriptionServer

from .auth import load_auth_info, get_socket_context
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

    # Websockets -----------------------------------------------------

    sockets = Sockets(app)
    app.app_protocol = lambda environ_path_info: 'graphql-ws'

    class SubscriptionServer(GeventSubscriptionServer):
        def on_connect(self, connection_context, payload):
            logger.debug('SubscriptionServer.on_connect(%s, %s)',
                         repr(connection_context), repr(payload))

            # TODO: is there a better way to pass context down, without
            # having to inject stuff into the connection context class??
            connection_context.auth_context = get_socket_context(payload)

        def get_graphql_params(self, connection_context, payload):
            _params = super().get_graphql_params(connection_context, payload)
            return {
                **_params,
                'context_value': connection_context.auth_context,
            }

    subscription_server = SubscriptionServer(schema)

    @sockets.route('/subscriptions')
    def echo_socket(ws):
        # context = get_socket_context(ws)
        # logger.debug('Socket: handling %s (%s)', repr(ws), repr(context))
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
