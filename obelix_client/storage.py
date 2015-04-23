import json


class Storage(object):
    def __init__(self, prefix=None, timeout=300):
        self.prefix = prefix
        self.storage = {}

    def get(self, key):
        """
        Get value on key
        """
        return self.storage.get(key, None)

    def getFromTable(self, table, key):
        storageKey = "{0}::{1}".format(table, key)

        return self.get(storageKey)

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
    def __init__(self, prefix=None, timeout=300):
        self.prefix = prefix
        self.storage = {}

    def get(self, key, value):
        if isinstance(value, dict):
            # TODO: improve error check
            result = json.loads(self.get(key))

        if isinstance(value, dict):
            # FIXME: error checks
            value = json.dumps(value)
