

class PyRedis(object):
    """ Redis in Python for testing """

    def __init__(self, store=None):
        if store:
            self.store = store
            self.store_timeout = {}
        else:
            self.store = {}
            self.store_timeout = {}

    def get(self, key):
        """
        Get value on key
        :param key:
        :return:
        """
        try:
            if key in self.store_timeout:
                if time() > self.store_timeout[key]:
                    return None

            return self.store[key]
        except KeyError:
            return None

    def set(self, key, value, timeout=None):
        """
        Sets value on key
        :param key:
        :param value:
        :param timeout:
        :return:
        """
        self.store[key] = value

        if timeout:
            self.store_timeout[key] = time() + timeout

        return self.store[key]

    def lpush(self, key, value):
        """
        Left push value to the *queue* key
        :param key:
        :param value:
        :return:
        """
        if key not in self.store:
            self.store[key] = deque()

        self.store[key].appendleft(value)

    def rpush(self, key, value):
        """
        Right push value to the *queue* key

        :param key:
        :param value:
        :return:
        """
        if key not in self.store:
            self.store[key] = deque()

        self.store[key].append(value)

    def rpop(self, key):
        """
        :param key: Right pop value from the *queue* key
        :return:
        """
        try:
            return self.store[key].pop()
        except (KeyError, IndexError):
            return None

    def lpop(self, key):
        """
        :param key: Left pop value from the *queue* key
        :return:
        """
        try:
            return self.store[key].popleft()
        except (KeyError, IndexError):
            return None


