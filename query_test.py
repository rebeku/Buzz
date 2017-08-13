import unittest
from query_users import industry, read_industry

class follower:
    def __init__(self, friends):
        self.friends_list = friends
        self.screen_name = "testing"
    def friends(self):
        return self.friends_list

class friend:
    def __init__(self, screen_name):
        self.screen_name = screen_name
        self.followers_count = 1

class mock_api:
    def __init__(self):
        pass
    def followers(self, id):
        return([follower([friend("f0"), friend("f1")])])

class QueryTestCase(unittest.TestCase):
    def set_up(self):
        mock = industry("mock.json")
        mock.api = mock_api()
        mock.add("Hello", 0, 1)
        mock.next()
        return mock
    def test_add_data(self):
        mock = self.set_up()
        assert len(mock.ids) == 3, "Failed to save correct friends for follower."
        user = mock.q.pop()
        assert user.id == "f0", "Q not returning correct screen names in FIFO order"
        assert user.gen == 1, "Q fails to track generations"
    def test_save(self):
        mock = self.set_up()
        mock.save()
        mock2 = read_industry("mock.json3")
        assert len(mock.ids) == 3 and mock.q.pop().id == "f0", "Not saving correct data"

def suite():
   suite = unittest.TestSuite()
   suite.addTest(QueryTestCase("test_add_data"))
   suite.addTest(QueryTestCase("test_save"))
   return suite

if __name__ == "__main__":
    suite = suite()
    unittest.main()
