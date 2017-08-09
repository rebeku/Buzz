import json
from fifo import Queue
import time
import tweepy
from collections import Counter
from threading import Thread

def build_api(authFile):
    with open(authFile, "r") as f:
        tokens = json.load(f)
        auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
        auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])
        return tweepy.API(auth)

"""
Track Twitter screen names associated with an industry
"""
class industry:
    def __init__(self, fName):
        self.q = Queue()   # track next ids in the industry to look up on Twitter
        self.ids = Counter() # remember all ids identified with industry
        self.friends_lim = 15
        self.api = build_api(".auth")
        self.name = fName
    """
    add a new Twitter screen name to the industry.
    """
    def add(self, id):
        self.q.push(id)
        self.ids[id] += 1
    """
    Generate next batch of screen_names
    """
    def next(self):
        id = self.q.pop()
        print("Finding neighbors of {}".format(id))
        self.add_neighbors(id)
    """
    Find users that are neighbors of a specific user
    (i.e. users that follow id will follow id2)
    """
    def add_neighbors(self, id):
        followers = self.api.followers(id)
        for follower in followers:
            if self.friends_lim == 0:
                self.wait()
            friends = self.get_friends(follower)
            print("Saved friends of {} to queue.".format(follower.screen_name))
            for friend in friends:
                name = friend.screen_name
                if name != id:
                    self.add(friend.screen_name)
    def save(self):
        q = industry.q.to_list()
        ids = dict(industry.ids)
        json.dump({"q":q, "ids":ids}, self.name)
    def wait(self):
        print("Hit rate limit.  Sleeping for 15 minutes. *Snore*")
        t = Thread(target=self.save)
        time.sleep(900)
        self.friends_lim = 15
    def get_friends(self, follower):
        try:
            self.friends_lim += -1
            friends = follower.friends()
            return friends
        except tweepy.error.RateLimitError:
            self.wait()
            return self.get_friends(followers)
        except tweepy.error.TweepError:
            # user has protected tweets
            return []

def save(industry, fName):
    # TODO: rewrite as method for industry
    q = industry.q.to_list()
    ids = dict(industry.ids)
    data = {"q":q, "ids":ids}
    with open(fName, "w") as f:
        json.dump(data, f)
    industry.q = Queue(q)

def read_industry(fName):
    with open(fName, "r") as f:
        data = json.load(f)
    ind = industry(fName)
    ind.q = Queue(data["q"])
    ind.ids = Counter(data["ids"])
    return ind


"""
Source: \http://www.academy-cube.com/10-tech-twitter-accounts-you-have-to-follow/
"""

tech_starters = ["TechCrunch", "WIRED", "TheNextWeb", "mashabletech", "scrawford", "pogue", "timoreilly", "cdixon", "google", "HP"]
tech = industry("tech.json")

for starter in tech_starters:
    tech.add(starter)

while True:
    tech.next()
