
from obelix_client.queue import RedisQueue
from obelix_client.storage import RedisMock
import json

class TestQueue(object):

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        pass

    def test_RedisMockQueue_lpush_rpop(self):
        queue = RedisMock()

        data1 = {"test": [1,2,3]}
        data2 = [1,2,3,]
        queue.lpush("q1", 111111)
        queue.lpush("q2", 222222)
        queue.lpush("q1", data1)
        queue.lpush("q2", data2)
        queue.lpush("q1", 555555)
        queue.lpush("q2", 666666)

        assert queue.rpop("q1") == 111111
        assert queue.rpop("q1") == data1
        assert queue.rpop("q1") == 555555

        assert queue.rpop("q2") == 222222
        assert queue.rpop("q2") == data2
        assert queue.rpop("q2") == 666666


    def test_RedisQueue_lpush_rpop_with_encoder_prefix(self):
        queue = RedisQueue(RedisMock(), prefix='pre::', encoder=json)

        data1 = {"test": [1,2,3]}
        data2 = [1,2,3,]
        queue.lpush("q1", 111111)
        queue.lpush("q2", 222222)
        queue.lpush("q1", data1)
        queue.lpush("q2", data2)
        queue.lpush("q1", 555555)
        queue.lpush("q2", 666666)

        assert queue.rpop("q1") == 111111
        assert queue.rpop("q1") == data1
        assert queue.rpop("q1") == 555555

        assert queue.rpop("q2") == 222222
        assert queue.rpop("q2") == data2
        assert queue.rpop("q2") == 666666

    def test_RedisQueue_rpush_lpop_with_encoder_prefix(self):
        queue = RedisQueue(RedisMock(), prefix='pre::', encoder=json)

        data1 = {"test": [1,2,3]}
        data2 = [1,2,3,]
        queue.rpush("q1", 111111)
        queue.rpush("q2", 222222)
        queue.rpush("q1", data1)
        queue.rpush("q2", data2)
        queue.rpush("q1", 555555)
        queue.rpush("q2", 666666)

        assert queue.lpop("q1") == 111111
        assert queue.lpop("q1") == data1
        assert queue.lpop("q1") == 555555

        assert queue.lpop("q2") == 222222
        assert queue.lpop("q2") == data2
        assert queue.lpop("q2") == 666666



    def test_lpush_and_rpop(self):
        queue = RedisQueue(RedisMock())
        #  Fill queue One and Two
        for i in range(0, 12):
            queue.lpush("One", i)
            queue.lpush("Two", i+30)

        # Check
        for i in range(0, 12):
            assert queue.rpop("One") == i
            assert queue.rpop("Two") == i+30
