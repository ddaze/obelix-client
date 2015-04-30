

class RedisQueue(object):
    def __init__(self, redis, prefix=None, encoder=None):
        self.prefix = prefix
        self.encoder = encoder
        self.redis = redis

    def lpush(self, queue, value):
        if self.prefix:
            queue = "{0}{1}".format(self.prefix, queue)
        if self.encoder:
            value = self.encoder.dumps(value)

        # FIXME: Error check
        self.redis.lpush(queue, value)

    def rpush(self, queue, value):
        if self.prefix:
            queue = "{0}{1}".format(self.prefix, queue)
        if self.encoder:
            value = self.encoder.dumps(value)

        # FIXME: Error check
        self.redis.rpush(queue, value)

    def rpop(self, queue):
        # TODO: Exeception or None?
        if self.prefix:
            queue = "{0}{1}".format(self.prefix, queue)
        data = self.redis.rpop(queue)
        if self.encoder:
            data = self.encoder.loads(data)

        return data

    def lpop(self, queue):
        # TODO: Exeception or None?
        if self.prefix:
            queue = "{0}{1}".format(self.prefix, queue)
        data = self.redis.lpop(queue)
        if self.encoder:
            data = self.encoder.loads(data)

        return data
