
class Queue(object):
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
        #TODO: Exeception or None?
        pass

class RedisQueue(Queue):
    def __init__(self, redis):
        self.redis = redis

    def put(self, value):
        self.redis.rput(value)
