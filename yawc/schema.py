import logging
import random
from datetime import datetime

import graphene
from rx import Observable
from yawc.auth import get_token_for_credentials
from yawc.db.query.chat import get_message_by_id, list_messages, post_message
from yawc.db.query.user import get_user
from yawc.utils.dates import utcnow

from .auth import Unauthorized
from .queue import get_watch_observable, send_message

logger = logging.getLogger(__name__)


class User(graphene.ObjectType):
    name = graphene.String()


class Message(graphene.ObjectType):
    id = graphene.String()
    timestamp = graphene.DateTime()
    text = graphene.String()
    channel = graphene.String()
    user = graphene.Field(User)
    user_id = graphene.Int()

    def resolve_user(self, info):
        try:
            # Allow passing a user object directly
            if self.user:
                return self.user
        except AttributeError:
            pass
        return get_user(self.user_id)


class Messages(graphene.ObjectType):
    edges = graphene.List(Message)


class Query(graphene.ObjectType):

    messages = graphene.Field(
        Messages,
        channel=graphene.String(required=True))

    def resolve_messages(self, info, channel):
        user = info.context.auth_info.user

        if not user:
            raise Unauthorized()

        return Messages(edges=[
            Message(id=0,
                    timestamp=datetime.utcnow(),
                    channel=channel,
                    text='Hello, {}! Welcome to #{}.'
                    .format(user.name, channel),
                    user=User(name='Chat bot')),
            *list_messages(channel),
        ])


class PostMessage(graphene.Mutation):

    class Arguments:
        channel = graphene.String(required=True)
        text = graphene.String(required=True)

    ok = graphene.Boolean()
    message_id = graphene.Int()

    def mutate(self, info, channel, text):
        user = info.context.auth_info.user

        if not user:
            raise Unauthorized()

        message = post_message(channel, text, user_id=user.id)
        send_message(message)
        return PostMessage(ok=True, message_id=message.id)


class Authenticate(graphene.Mutation):

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()
    token = graphene.String()

    def mutate(self, info, email, password):
        token = get_token_for_credentials(email, password)
        if token:
            return Authenticate(ok=True, token=token.decode())
        return Authenticate(ok=False, token=None)


class Mutations(graphene.ObjectType):
    post_message = PostMessage.Field()
    auth = Authenticate.Field()


class RandomType(graphene.ObjectType):
    seconds = graphene.Int()
    random_int = graphene.Int()


class Subscription(graphene.ObjectType):

    new_messages = graphene.Field(
        Message, channel=graphene.String(required=True))

    def resolve_new_messages(root, info, channel):
        logger.info('----- RESOLVE NEW MESSAGES called: %s %s %s',
                    repr(root), repr(info), channel)

        # FIXME check authorization!
        # Can we access HTTP headers?

        return (
            get_watch_observable(channel)
            .map(lambda msg: get_message_by_id(msg['id'])))


schema = graphene.Schema(
    query=Query,
    mutation=Mutations,
    subscription=Subscription)
