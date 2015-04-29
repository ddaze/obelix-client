import json
import msgpack


class StorageProxy(object):
    """ Generic Storage:
        Your storage only has to support get, and set with default values
    """
    def __init__(self, storage, prefix=None, encoder=None):
        """
        :encoder: has to support load() and dump()
        """
        self.prefix = prefix
        self.encoder = encoder
        self.storage = storage

    def get(self, key, default=None):
        if self.prefix:
            key = "{0}{1}".format(self.prefix, key)

        data = self.storage.get(key, default)
        if self.encoder:
            return self.encoder.load(data)

        return data

    def set(self, key, value):
        if self.prefix:
            key = "{0}{1}".format(self.prefix, key)

        if self.encoder:
            value = self.encoder.dump(value)

        if hasattr(self.storage, 'set'):
            self.storage.set(key, value)
        else:
            self.storage[key] = value


class RedisStorage(StorageProxy):
    """ Warapper for Redis:
        Takes care of the Timeout
    """
    def __init__(self, storage, prefix=None, encoder=None):
        super(RedisStorage, self).__init__(storage, prefix, encoder)

    def get(self, key, default=None):
        # TODO: Timeout stuff
        super(RedisStorage, self).get(key, default)

    def set(self, key, value):
        # TODO: Timeout stuff
        super(RedisStorage, self).set(key, value)


class RESTStorage(object):

    def __init__(self, base_url=None, ):
        pass
        # set_url or get_ulr
        # base is not None

    def get(self, key):
        return requests.get(self.url.format(key=key), ).json
