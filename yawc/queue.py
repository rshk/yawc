import json
import logging
import os
import threading
import time

# import gevent
import redis as Redis
from gevent import monkey
from rx import Observable

monkey.patch_all()


logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
REDIS_CHAN_MESSAGES = 'messages'  # Todo use one redis channel per channel?


redis_client = Redis.from_url(REDIS_URL)


class RedisPubsubObservable:

    def __init__(self, redis_url, redis_channel):
        self._redis_url = redis_url
        self._redis_channel = redis_channel
        self._observable = None

    def _connect(self):
        """Make sure connection is not shared across gevent thread thingies
        """
        # return Redis.from_url(self._redis_url)
        assert self._redis_url == REDIS_URL
        return redis_client

    def publish(self, data):
        redis = self._connect()
        redis.publish(self._redis_channel, json.dumps(data))

    def get_observable(self):
        logger.debug('GET OBSERVABLE [chan: {}]'
                     .format(self._redis_channel))
        if not self._observable:
            logger.debug('Create new observable')
            self._observable = self.create_observable()
        return self._observable

    def create_observable(self):
        # items = self.watch()
        # return Observable.from_iterable(items)

        def listen_to_redis_async(observable):

            logger.debug('===> Starting Redis SUBSCRIBE thread')

            def thread_callback():

                logger.debug('THREAD CALLBACK STARTED')

                redis = self._connect()
                pubsub = redis.pubsub()
                pubsub.subscribe(self._redis_channel)

                for m in pubsub.listen():

                    if m['type'] != 'message':
                        logger.debug('<<< Redis pub/sub CTL: %s', repr(m))
                        continue

                    logger.debug('<<< Redis pub/sub MSG: %s', repr(m))
                    data = json.loads(m['data'])
                    observable.on_next(data)
                    logger.debug('>>> Redis pub/sub sent: %s', repr(data))

                logger.debug('THREAD CALLBACK FINISHED')

            t = threading.Thread(target=thread_callback)
            t.setDaemon(True)
            t.start()

        # NOTE: the function will be called for every new subscriber,
        # creating more and more threads listening to Redis.
        # We actually want to somehow share events coming from the *one*
        # thread attached to Redis...
        return Observable.create(listen_to_redis_async)


messages_queue = RedisPubsubObservable(REDIS_URL, REDIS_CHAN_MESSAGES)


def send_message(message):
    messages_queue.publish({
        'id': message.id,
        # 'timestamp': message.timestamp,
        # 'user_id': message.user_id,
        'channel': message.channel,
        'text': message.text,
    })


def get_watch_observable(channel):
    return (
        messages_queue
        .get_observable()
        .filter(lambda msg: msg['channel'] == channel))
