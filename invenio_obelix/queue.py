class RedisQueue(object):
    def __init__(self, redis):
        self.redis = redis

    def put(self, value):
        self.redis.rput(value)
