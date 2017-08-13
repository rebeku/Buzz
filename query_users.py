import json
from fifo import Queue
import time
import tweepy
from math import log10
from threading import Thread

def build_api(authFile):
    with open(authFile, "r") as f:
        tokens = json.load(f)
        auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
        auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])
        return tweepy.API(auth)

class twitter_user(object):
    def __init__(self, id, gen, followers):
        self.id = id
        self.gen = gen
        self.followers = followers

"""
counter tracks the number of times each twitter user has been followed in our local dataset
and the number of times that user has been followed at all.  Frequency counts for each user are
adjusted by the log-scale proportion of followers that are in local dataset.
"""
class counter(dict):
    def __init__(self, data= {}):
        self = data
    def add(self, user):
        id = user.id
        if id in self:
            self[id]["local"] += 1
        else:
            self[id] = {"local": 1, "total": user.followers}
    def weights(self):
        weighted = {}
        for k, v in self.items():
            weighted[k] = v["local"] * log10(v["local"] / v["total"])
        return weighted

"""
Track Twitter screen names associated with an industry
"""
class industry(object):
    def __init__(self, fName):
        self.q = Queue()   # track next ids in the industry to look up on Twitter
        self.ids = counter() # remember all ids identified with industry
        self.friends_lim = 15
        self.api = build_api(".auth")
        self.name = fName
    """
    add a new Twitter screen name to the industry.
    """
    def add(self, user):
        self.q.push(user)
        self.ids.add(user)
    """
    Generate next batch of screen_names
    """
    def next(self):
        user = self.q.pop()
        print("Finding neighbors of {}".format(user.id))
        self.add_neighbors(user)
    """
    Find users that are neighbors of a specific user
    (i.e. users that follow id will follow id2)
    """
    def add_neighbors(self, user):
        followers = self.api.followers(user.id)
        for follower in followers:
            if self.friends_lim == 0:
                self.wait()
            friends = self.get_friends(follower)
            print("Saved friends of {} to queue.".format(follower.screen_name))
            for friend in friends:
                if friend.screen_name != user.id:
                    f_user = twitter_user(friend.screen_name, user.gen + 1, friend.followers_count)
                    self.add(f_user)
    def save(self):
        try:
            q = [(user.id, user.gen, user.followers) for user in self.q.to_list(copy=True)]
            print(q)
        except:
            q = []
        try:
            ids = dict(self.ids)
        except:
            ids = {}
        #ids will grow as code runs.  This may be used to reconstruct the order of files.
        fName = self.name + str(len(self.ids))
        with open(fName, "w") as f:
            json.dump({"q":q, "ids":ids}, f)
        print("Saved backup of data as {}.".format(fName))
    def wait(self):
        print("Hit rate limit.  Sleeping for 15 minutes. *Snore*")
        t = Thread(target=self.save)
        t.start()
        time.sleep(900)
        self.friends_lim = 15
    def get_friends(self, follower):
        try:
            self.friends_lim += -1
            friends = follower.friends()
            return friends
        except tweepy.error.RateLimitError:
            self.wait()
            return self.get_friends(follower)
        except tweepy.error.TweepError:
            # user has protected tweets
            return []

def read_industry(fName):
    with open(fName, "r") as f:
        data = json.load(f)
    ind = industry(fName)
    q = [twitter_user(u[0], u[1], u[2]) for u in data["q"]]
    ind.q = Queue(q)
    ind.ids = counter(data["ids"])
    return ind


"""
Source: \http://www.academy-cube.com/10-tech-twitter-accounts-you-have-to-follow/
"""
tech_starters = [("TechCrunch", 9480348), ("WIRED", 9439670), ("TheNextWeb", 1847417), ("mashabletech", 676412), ("scrawford", 20404),( "pogue", 1563905), ("timoreilly", 1988327), ("cdixon", 565563), ("google", 18616185), ("HP", 1055688)]
tech = industry("tech.json")

if __name__ == "__main__":
    for starter in tech_starters:
        user = twitter_user(starter[0], 0, starter[1])
        tech.add(user)

    while True:
        tech.next()
