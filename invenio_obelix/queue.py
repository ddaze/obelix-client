
class Queue(object):
    def __init__(self, prefix=None, timeout=None):
        self.prefix = None
        self.queues = {}

    def lpush(self, queue, value):
        if not self.queues.get(queue, None):
            # Create queue
            self.queues[queue] = []
        self.queues[queue].insert(0, value)

    def lpushToTabel(self, table, queue, value):
        key = "{0}::{1}".format(table, queue)
        self.lpush(key, vaule)

    def rpush(self, queue, value):
        if not self.queues.get(queue, None):
            # Create queue
            self.queues[queue] = []
        self.queues[queue].append(value)

    def rpushToTabel(self, table, queue, value):
        key = "{0}::{1}".format(table, queue)
        self.rpush(key, vaule)

    def rpop(self, queue):
        #TODO: Exeception or None?
        pass

class RedisQueue(Queue):
    def __init__(self, redis):
        self.redis = redis

    def put(self, value):
        self.redis.rput(value)
