import json
import msgpack


class Queues(object):
    def __init__(self, prefix=None):
        self.prefix = None
        self.queues = {}

    def lpush(self, queue, value):
        if not self.queues.get(queue, None):
            # Create queue
            self.queues[queue] = []
        self.queues[queue].insert(0, value)

    def rpush(self, queue, value):
        if not self.queues.get(queue, None):
            # Create queue
            self.queues[queue] = []
        self.queues[queue].append(value)

    def rpop(self, queue):
        # TODO: Exeception or None?
        return self.queues[queue].pop()

    def lpop(self, queue):
        # TODO: Exeception or None?
        return self.queues[queue].pop(0)


class RedisQueue(Queues):
    def __init__(self, redis, prefix=None):
        self.prefix = prefix
        self.redis = redis

    def lpush(self, queue, value):
        if self.prefix:
            queue = "{0}::{1}".format(self.prefix, queue)
        data = msgpack.packb(value)

        # FIXME: Error check
        self.redis.lpush(queue, data)

    def rpush(self, queue, value):
        if self.prefix:
            queue = "{0}::{1}".format(self.prefix, queue)
        data = msgpack.packb(value)

        # FIXME: Error check
        self.redis.rpush(queue, data)

    def rpop(self, queue):
        # TODO: Exeception or None?
        if self.prefix:
            queue = "{0}::{1}".format(self.prefix, queue)
        data = msgpack.unpackb(self.redis.rpop(queue))

        return data

    def lpop(self, queue):
        # TODO: Exeception or None?
        if self.prefix:
            queue = "{0}::{1}".format(self.prefix, queue)
        data = msgpack.unpackb(self.redis.lpop(queue))

        return data
