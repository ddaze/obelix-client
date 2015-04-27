import json
import msgpack


class Storage(object):
    def __init__(self, prefix=None, timeout=300):
        self.prefix = prefix
        self.storage = {}

    def get(self, key, default=None):
        """
        Get value on key
        """
        return self.storage.get(key, default)

    def getFromTable(self, table, key, default=None):
        storageKey = "{0}::{1}".format(table, key)

        return self.get(storageKey, default)

    def set(self, key, value):
        """
        Sets value on a key
        """
        # TODO: Maybe exceptions
        self.storage[key] = value

    def setToTable(self, table, key, value):
        storageKey = "{0}::{1}".format(table, key)

        return self.set(storageKey, value)


class RedisStorage(Storage):
    def __init__(self, redis, prefix=None):
        self.prefix = prefix
        self.storage = {}
        self.redis = redis

    def get(self, key, default=None):
        if self.prefix:
            key = "{0}::{1}".format(self.prefix, key)
        data = msgpack.unpackb(self.redis.get(key))

        # FIXME: Default value, error?
        return data

    def set(self, key, value):
        if self.prefix:
            key = "{0}::{1}".format(self.prefix, key)
        data = msgpack.packb(value)
        self.redis.set(key, value)
