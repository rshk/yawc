import json
import logging
import os
import threading
import time

import gevent
import redis as Redis
from gevent import monkey
from rx import Observable

monkey.patch_all()


logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
REDIS_CHAN_MESSAGES = 'messages'  # Todo use one redis channel per channel?


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
        # items = self.watch()
        # return Observable.from_iterable(items)

        logger.debug('GET OBSERVABLE [chan: {}]'.format(self._redis_channel))

        def listen_to_redis_async(observable):

            logger.debug('LISTEN TO REDIS ASYNC')

            def thread_callback():

                logger.debug('THREAD CALLBACK STARTED')

                redis = self._connect()
                pubsub = redis.pubsub()
                pubsub.subscribe(self._redis_channel)

                for m in pubsub.listen():

                    if m['type'] != 'message':
                        logger.debug('REDIS PUBSUB: %s', repr(m))
                        continue

                    logger.debug('REDIS MESSAGE %s', repr(m))
                    data = json.loads(m['data'])
                    observable.on_next(data)
                    logger.debug('====> SENT %s', repr(data))

                logger.debug('THREAD CALLBACK FINISHED')

            t = threading.Thread(target=thread_callback)
            t.setDaemon(True)
            t.start()

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
