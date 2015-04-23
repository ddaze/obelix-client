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

    def getFromJson(self, key):
        """
        Get that contains json and parse it into a dict
        :raises
            TypeError: TypeError: expected string or buffer, if anything else than a str is stored
            ValueError: No JSON object could be decoded (invalid json format)
        """
        result = None
        # TODO: improve error check
        result = json.loads(self.get(key))

        return result

    def set(self, key, value):
        """
        Sets value on a key
        """
        # TODO: Maybe exceptions
        self.store[key] = value

    def setToTable(self, table, key, value):
        storageKey = "{0}::{1}".format(table, key)

        return self.set(storageKey, value)


class RedisStorage(Storage):
    def __init__(self, prefix=None, timeout=300):
        self.prefix = prefix
        self.storage = {}





