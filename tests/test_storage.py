
from obelix_client.storage import StorageProxy, RedisStorage, RedisMock
import json

class TestStorageDict:
    def setUp(self):
        self.storage = StorageProxy()

    def test_set_and_get(self):
        storage = StorageProxy({})
        storage.set("theKey", "theValue")
        storage.set("theKey2", "theValue2")
        assert storage.get("theKey2") == "theValue2"
        assert storage.get("theKey") == "theValue"
        assert storage.get("noKey") == None

    def test_set_and_get_with_prefix_encoder(self):
        storage = StorageProxy({}, prefix='pre::', encoder=json)
        storage.set("theKey", "theValue")
        storage.set("theKey2", "theValue2")
        assert storage.get("theKey2") == "theValue2"
        assert storage.get("theKey") == "theValue"
        assert storage.get("noKey") == None

    def test_Redis_set_and_get_with_prefix_encoder(self):
        storage = RedisStorage(RedisMock(), prefix='pre::', encoder=json)
        storage.set("theKey", "theValue")
        storage.set("theKey2", "theValue2")
        assert storage.get("theKey2") == "theValue2"
        assert storage.get("theKey") == "theValue"
        assert storage.get("noKey") == None

