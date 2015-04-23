
from obelix_client.storage import Storage
from obelix_client.queues import Queues

class TestStorageDict:
    def setUp(self):
        self.storage = Storage()

    def test_set_and_get(self):
        storage = Storage()
        storage.set("theKey", "theValue")
        storage.set("theKey2", "theValue2")
        assert storage.get("theKey2") == "theValue2"
        assert storage.get("theKey") == "theValue"
        assert storage.get("noKey") == None

    def test_setToTable_and_getToTable(self):
        storage = Storage()
        storage.setToTable("tab1", "theKey", "theValue")
        storage.setToTable("tab2", "theKey2", "theValue2")
        storage.setToTable("tab2", "theKey", "theValue")
        assert storage.getFromTable("tab1", "theKey") == "theValue"
        assert storage.getFromTable("tab2", "theKey2") == "theValue2"
        assert storage.getFromTable("tab2", "theKey") == "theValue"
        assert storage.getFromTable("tab1", "theKey2") == None


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
