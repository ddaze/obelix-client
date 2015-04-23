import json


class Queues(object):
    def __init__(self, prefix=None, timeout=None):
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
    def __init__(self, redis):
        self.redis = redis

    def lpush(self, value):
        if isinstance(value, dict):
            # TODO: error check
            value = json.dumps(value)
        self.redis.rput(value)
