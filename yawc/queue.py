import json
import logging
import os
import time

import redis as Redis
from rx import Observable

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
REDIS_CHAN_MESSAGES = 'messages'


class RedisPubsubObservable:

    def __init__(self, redis_url, redis_channel):
        self._redis_url = redis_url
        self._redis_channel = redis_channel

    def _connect(self):
        """Make sure connection is not shared across gevent thread thingies
        """
        return Redis.from_url(self._redis_url)

    def publish(self, data):
        redis = self._connect()
        redis.publish(self._redis_channel, json.dumps(data))

    def watch(self):
        """Watch for messages in the queue.

        Not that we cannot use pubsub.listen() as that would block the
        thread, preventing gevent context-switches.

        Instead, we just poll for messages and sleep() in between..
        """

        redis = self._connect()
        pubsub = redis.pubsub()
        pubsub.subscribe(self._redis_channel)

        while True:
            msg = pubsub.get_message()
            if not msg:
                # Be nice on the system
                time.sleep(.001)
                continue

            if msg['type'] == 'message':
                logger.debug('RECV MSG: %s', repr(msg))
                data = json.loads(msg['data'])
                yield data

    def get_observable(self):
        items = self.watch()
        return Observable.from_iterable(items)


messages_queue = RedisPubsubObservable(REDIS_URL, REDIS_CHAN_MESSAGES)


def send_message(channel, text):
    logger.debug('SEND MSG [%s]: %s', channel, text)
    messages_queue.publish({'channel': channel, 'text': text})


def get_watch_observable(channel):
    return (
        messages_queue
        .get_observable()
        .filter(lambda msg: msg['channel'] == channel))
