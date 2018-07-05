import random
from datetime import datetime

import graphene
from rx import Observable
from yawc.auth import get_token_for_credentials

from .queue import get_watch_observable, send_message


class User(graphene.ObjectType):
    name = graphene.String()


class Message(graphene.ObjectType):
    id = graphene.String()
    timestamp = graphene.DateTime()
    text = graphene.String()
    channel = graphene.String()
    user = graphene.Field(User)


class Messages(graphene.ObjectType):
    edges = graphene.List(Message)


class Query(graphene.ObjectType):

    messages = graphene.Field(
        Messages,
        channel=graphene.String(required=True))

    def resolve_messages(self, info, channel):
        user = info.context.auth_info.user

        return Messages(edges=[
            Message(id=1,
                    timestamp=datetime.utcnow(),
                    channel=channel,
                    text='Hello, {}! Welcome to #{}.'
                    .format(user.name, channel),
                    user=User(name='Chat bot')),
        ])


class PostMessage(graphene.Mutation):

    class Arguments:
        channel = graphene.String(required=True)
        text = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, channel, text):
        send_message(channel, text)
        return PostMessage(ok=True)


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

    count_seconds = graphene.Int(up_to=graphene.Int())

    def resolve_count_seconds(root, info, up_to=5):
        return (
            Observable
            .interval(1000)
            .map(lambda i: "{0}".format(i))
            .take_while(lambda i: int(i) <= up_to))

    random_int = graphene.Field(RandomType)

    def resolve_random_int(root, info):
        return (
            Observable
            .interval(1000)
            .map(lambda i:
                 RandomType(seconds=i, random_int=random.randint(0, 500))))

    messages = graphene.Field(Message, channel=graphene.String())

    def resolve_messages(root, info, channel):
        return (
            get_watch_observable(channel)
            # Observable.interval(1000)

            .map(lambda msg: Message(channel=msg['channel'], text=msg['text']))
        )


schema = graphene.Schema(
    query=Query,
    mutation=Mutations,
    subscription=Subscription)
