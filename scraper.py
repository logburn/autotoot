import os
import logging
import json
from reddit import reddit_scraper as reddit
from time import sleep

class scraper:
    def __init__(self, service, config, neuter=False):
        # error checking
        scrapers = ["reddit"]
        if service.lower() not in scrapers:
            logging.error(f"Scraper {service} invalid. Choose one of {', '.join(scrapers)}")
            return None
        # make sure necessary filestructure is in place
        if not os.path.isdir("temp"): os.mkdir("temp")
        if not os.path.exists("savefile.json"):
            f = open("savefile.json", "w+")
            f.write("{}")
            f.close()
        # set object variables
        self.service = service
        self.neuter = neuter
        # login to service
        if service == "reddit": self.login = reddit(config)

    ### WRAPPER METHODS
    def scrape(self, place, limit=10):
        logging.warning(f"Scraping {self.service}: {place}... ")
        result = self.login.scrape(place, limit)
        logging.warning(f"Done scraping {self.service}: {place}.")
        return result

    # gets posts from a gives service's places (ie, multiple subreddits or feeds)
    def scrape_all(self, limit=10):
        return self.login.scrape_all(limit)

    # downloads a given post's media and return the locations
    def download(self, post):
        logging.warning(f"Downloading {post.id}... ")
        if not self.neuter: self.login.download(post)
        else: print(f"Neuter: would have downloaded {post} content")
        logging.warning(f"Done downloading {post.id}.")
        return result

    # downloads a list of post's media and returns a list of the locations
    def download_all(self, posts):
        post_ids = [p.id for p in posts]
        locations = []
        for post in post_ids:
            locations.append(self.login.download(post))
        return locations

    # creates the savefile for a list of posts.
    def remember(self):
        logging.warning(f"Remembering {self.service}...")
        self.login.remember()
        logging.warning(f"Remembered {self.service}.")
    
    # posts for each place if it has been a while
    def keep_lively(self):
        self.login.keep_lively()

    # posts a random post from the given place
    def random_post(self, place):
        logging.warning(f"Getting random post for {place}")
        return self.login.random_post(place)

    ### TOOTER METHODS
    # takes a toot and returns a dict of the text and media IDs
    def build_toot(self, masto, post):
        return self.login.build_toot(masto, post, neuter=self.neuter)

    # toots all posts in list
    def toot_posts(self, masto, posts):
        for post in posts:
            to_toot = self.build_toot(masto, post)
            masto.toot(to_toot["text"], to_toot["media"])
        return True
