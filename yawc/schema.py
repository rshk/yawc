import random
from datetime import datetime

import graphene
from rx import Observable
from werkzeug.exceptions import BadRequest, default_exceptions

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

    # hello = graphene.String(
    #     name=graphene.String(
    #         default_value="stranger",
    #         description='Name of the person to be greeted'),
    #     description='Returns a greeting for the specified person')

    # def resolve_hello(self, info, name):
    #     return 'Hello ' + name

    # error = graphene.String(
    #     code=graphene.Int(default_value=400),
    #     description='Returns the specified HTTP error')

    # def resolve_error(self, info, code):
    #     if code not in default_exceptions:
    #         raise BadRequest('Unsupported error code {}'.format(code))
    #     raise default_exceptions[code]

    messages = graphene.Field(
        Messages,
        channel=graphene.String(required=True))

    def resolve_messages(self, info, channel):
        user = User(name='Hello')
        return Messages(edges=[
            Message(id=1, timestamp=datetime.utcnow(),
                    channel='hello', text='It works!', user=user),
        ])


class PostMessage(graphene.Mutation):

    class Arguments:
        channel = graphene.String(required=True)
        text = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, channel, text):
        send_message(channel, text)
        return PostMessage(ok=True)


class Mutations(graphene.ObjectType):
    post_message = PostMessage.Field()


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
