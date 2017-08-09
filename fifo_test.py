import unittest
from fifo import Queue

class QueueTestCase(unittest.TestCase):
    def runTest(self):
        q = Queue([1, 2, 3, 4, 5])
        assert q.pop() == 1, "Incorrect head returned"
        assert q.pop() == 2, "Head not changed following pop."
        q.push(6)
        assert q.pop() == 3, "Push operation changes head."
        assert q.to_list(copy=True) == [4, 5, 6], "Incorrect list export"
        assert q.pop() == 4, "q failed to survive copying operation."

runner = unittest.TextTestRunner()
runner.run(QueueTestCase.runTest)
