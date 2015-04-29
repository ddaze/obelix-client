
from obelix_client.storage import StorageProxy
from obelix_client.queues import Queues

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


class TestQueueDict:
    def test_lpush_and_rpop(self):
        queues = Queues()
        #  Fill queue One and Two
        for i in range(0, 12):
            queues.lpush("One", i)
            queues.lpush("Two", i+30)

        # Check
        for i in range(0, 12):
            assert queues.rpop("One") == i
            assert queues.rpop("Two") == i+30
