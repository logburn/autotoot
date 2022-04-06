from helper import helper
import praw
import json
import time
import logging

class reddit_scraper:
    def __init__(self, config):
        self.login = praw.Reddit(
                client_id=config["reddit"]["client_id"],
                client_secret=config["reddit"]["client_secret"],
                password=config["reddit"]["password"],
                user_agent=config["reddit"]["user_agent"],
                username=config["reddit"]["username"])
        self.places = config["reddit"]["places"]
        savefile = open("savefile.json", "r")
        savefile = json.load(savefile)
        try: self.seent = savefile["reddit"]
        except: self.seent = {}
                

    ### REDDIT METHODS
    # gets posts from a given subreddit
    def scrape(self, sub, limit):
        # make sure self.seent has the sub, add if not
        if sub not in self.seent: self.seent[sub] = time.time()
        # get posts that aren't in seent list
        post_list = []
        posts = self.login.subreddit(sub).new(limit=limit)
        posts = helper.reddit_listify(posts)
        for p in posts[::-1]:
            if helper.ts_older(p.created, self.seent[sub]):
                break
            logging.info(f"Scraping post {p.id}")
            post_list.append(p)
            self.seent[sub] = p.created
        return post_list
    
    # scrapes all subreddits
    def scrape_all(self, limit):
        subposts = {}
        for place in self.places:
            subposts[place] = self.scrape(place, limit)
        return subposts
    
    # downloads a given post; media is stored in temp/post_id/n
    # returns a list of the stored file locations for that post
    def download(self, post):
        def make_gallery_urls():
            nonlocal post
            urls = []
            for m in post.media_metadata:
                mimetype = post.media_metadata[m]["m"]
                end = mimetype[mimetype.find("/")+1:]
                urls.append(f"https://i.redd.it/{m}.{end}")
            return urls
        # video is sketchy, sorta WIP but maybe impossible
        # to have consistently. this function does its best
        def try_video_urls(post):
            try:
                raw_url = post.media["video"]["fallback_url"]
                return [raw_url[:raw_url.find("?")]]
            except:
                try:
                    raw_url = post.media["reddit_video"]["fallback_url"]
                    return [raw_url[:raw_url.find("?")]]
                except:
                    return []
            return [] # should never be reached but just in case
        
        # get the media URLs in array
        urls = []
        post_type = helper.get_post_type(post)
        if post_type == "image":
            urls = [post.url]
        elif post_type == "video":
            urls = try_video_urls(post)
        elif post_type == "gallery":
            urls = make_gallery_urls()
        
        # download all media
        local_urls = []
        i = 0
        for url in urls:
            i += 1
            name = f"temp/{post.id}/{i}"
            logging.info(f"Downloading {url} ({i}/{len(urls)})")
            helper.download_media(url, name)
            local_urls.append(name)
        
        return local_urls
    
    # posts if it's been a while. checks each sub and 
    def keep_lively(self):
        for sub in self.places:
            if helper.been_awhile(self.seent[sub]):
                self.random_post(sub)

    # gets a random post from reddit
    def random_post(self, place):
        return self.login.subreddit(place).random()
    
    # creates the savefile for a list of posts.
    def remember(self):
        print(f"{self.seent}")
        savefile = json.load(open("savefile.json", "r"))
        savefile["reddit"] = self.seent
        savefile = json.dumps(savefile)
        with open("savefile.json", "w") as f:
            f.write(savefile)

    ### TOOTER METHODS
    # takes a toot and returns a dict of the text and media IDs
    def build_toot(self, masto, post):
        toot = {}
        toot["text"] = post.title
        if helper.get_post_type(post) == "video": toot["text"] += f"\n\n{post.url}"
        local_media = self.download(post)
        toot["media"] = masto.upload_all_media(local_media)
        return toot

    # toots all posts in list
    def toot_posts(self, masto, posts):
        for post in posts:
            to_toot = self.build_toot(masto, post)
            masto.toot(to_toot["text"], to_toot["media"])
        return True
