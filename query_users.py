import json
from fifo import Queue
import time
import tweepy
from collections import Counter

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
    def __init__(self):
        self.q = Queue()   # track next ids in the industry to look up on Twitter
        self.ids = Counter() # remember all ids identified with industry
        self.friends_lim = 15
        self.api = build_api(".auth")
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
            for friend in friends:
                self.add(friend.screen_name)
    def wait(self):
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


"""
Source: \http://www.academy-cube.com/10-tech-twitter-accounts-you-have-to-follow/
"""
tech_starters = ["TechCrunch", "WIRED", "TheNextWeb", "mashabletech", "scrawford", "pogue", "timoreilly", "cdixon", "google", "HP"]
tech = industry()

for starter in tech_starters:
    tech.add(starter)
