from mastodon import Mastodon
import praw
import requests
import os
import time
import json
import logging

'''
TODO:
  for deployment:
    - [x] Keep track of what has been scraped and tooted to not duplicate posts
    - [x] Download and posting of video files
    - [x] Make sure text-only reddit posts work
    - [x] Eternal looping, run script every 5 mins or something
    - [x] Different masto post structures for different post types (videos need links)

  extras:
    - [x] Import bot/scraper settings from file for automation
    - [ ] Updating from @mention toot
    - [ ] Improve debugging logging
       - [ ] Info logging
       - [ ] Error logging
    - [ ] Add twitter bot
    - [ ] Make this an installable (pip?) package
'''

# 

# Mastodon bot to post things
class bot():
    def __init__(self, config, debug=False):
        self.debug = debug
        self.masto = Mastodon(access_token=config["mastodon"]["access_token"], api_base_url=config["mastodon"]["host"])
    
    # uploads media to mastodon, returns the mastodon ID
    # specify mimetype of video files as "video/mp4" to avoid error
    def upload_media(self, filename, mimetype=None):
        if self.debug: print(f"Uploading media {filename}")
        return self.masto.media_post(filename, mime_type=mimetype)
    
    # uploads all given media
    def upload_all_media(self, filenames):
        ids = []
        for fn in filenames:
            ids.append(self.upload_media(fn))
        return ids
    
    def toot(self, text, media=None):
        if self.debug: print(f"Posting:\n  Text: {text}\n  Media: {', '.join(media) if media != None else 'None'}")
        self.masto.status_post(text, media_ids=media)

# Reddit (maybe more in future) scaper to get postsn future) scaper to get posts
# parameters:
#   service: one of ["reddit"]
#   config: dict of config variables
class scraper():
    def __init__(self, service, config, debug=False):
        # dev
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger().addHandler(console)
        self.current_services = ["reddit"]
        # error checkitootng
        if service.lower() not in self.current_services:
            logging.error("Service invalid")
            return None
        # login to service
        if service == "reddit":
            self.login = praw.Reddit(
                client_id=config["reddit"]["client_id"],
                client_secret=config["reddit"]["client_secret"],
                password=config["reddit"]["password"],
                user_agent=config["reddit"]["user_agent"],
                username=config["reddit"]["username"])
        # make sure necessary filestructure is in place
        needed_directories = ["temp", "save", f"save/{service}"]
        for d in needed_directories:
            if not os.path.isdir(d): os.mkdir(d)
        if not os.path.exists(f"save/{service}"):
            open(f"save/{service}", "w+")
            f.close()
        # set object variables
        self.service = service
        self.debug = debug
        self.places = config[service]["places"]
        # seent it list is a little more complicated
        self.seent = {}
        for f in os.listdir(f"save/{service}"):
            savefile = open(f"save/{service}/{f}", "r").read().split("\n")
            self.seent[f.split("/")[-1]] = [item for item in savefile] # dict faster


    ### HELPER METHODS
    # helper method to clean out folder (delete all contents)
    # expected structure: [["temp/a/1", "temp/a/2"], [], [], ["temp/e/1"]]
    def remove_folders(self, folders_list):
        for folder in folders_list:
            if self.debug: print(f"Clearing folder {folder}")
            for file in folder:
                os.remove(file)
            if len(folder) > 0:
                subfolder = "/".join(folder[0].split("/")[:-1])
                os.rmdir(subfolder)

    # helper method to download media
    def download_media(self, url, filename):
        # get file first
        if self.debug: print(f"Downloading {url} info {filename}")
        resp = requests.get(url)
        if resp.ok:
            # make sure directory structure exists
            structure = filename.split("/")
            for i in range(len(structure[:-1])):
                d = "/".join(structure[0:i+1])
                if not os.path.isdir(d): os.mkdir(d)
            # write the downloaded content to file
            with open(filename, "wb+") as f:
                f.write(resp.content)
    
    # reddit helper method to return the post type
    def get_post_type(self, post):
        if post.url[8] == 'i': return "image"
        if post.url[8] == 'v': return "video"
        if post.url[23:30] == "gallery": return "gallery"
        return "unknown"
    
    # helper to save a list with a limit to a savefile
    def create_savefile(self, places, limit):
        # write to seent list memory and return posts
        for place in places:
            if self.debug: print(f"Creating savefile save/{self.service}/{place}")
            new_seent = [k for k in self.seent[place] if k != ""]
            if len(new_seent) > limit: new_seent = new_seent[:limit]
            open(f"save/{self.service}/{place}", "w").write("\n".join(new_seent))
    

    ### REDDIT METHODS
    # gets posts from a given subreddit
    def reddit_scrape(self, sub_name, limit):
        # make sure seent list can store files for this sub
        if sub_name not in self.seent:
            self.seent[sub_name] = []
        if not os.path.exists(f"save/{self.service}/{sub_name}"):
            f = open(f"save/{self.service}/{sub_name}", "w+")
            f.close()
        # get posts that aren't in seent list
        post_list = []
        for p in self.login.subreddit(sub_name).new(limit=limit):
            if p.id not in self.seent[sub_name]:
                if self.debug: print(f"Scraping post {p.id}")
                post_list.append(p)
                self.seent[sub_name] = [p.id] + self.seent[sub_name]
        return post_list

    # gets posts form all subreddits
    def reddit_scrape_all(self, sub_names, limit):
        subposts = {}
        for sub in sub_names:
            subposts[sub] = self.reddit_scrape(sub, limit)
        return subposts
    
    # downloads a given post; media is stored in temp/post_id/n
    # returns a list of the stored file locations for that post
    def reddit_download(self, post):
        def make_gallery_urls():
            nonlocal post
            urls = []
            for m in post.media_metadata:
                mimetype = post.media_metadata[m]["m"]
                end = mimetype[mimetype.find("/")+1:]
                urls.append(f"https://i.redd.it/{m}.{end}")
            return urls
        
        # get the media URLs in array
        reddit_urls = []
        post_type = self.get_post_type(post)
        if post_type == "image":
            reddit_urls = [post.url]
        elif post_type == "video":
            raw_url = post.media["reddit_video"]["fallback_url"]
            reddit_urls = [raw_url[:raw_url.find("?")]]
        elif post_type == "gallery":
            reddit_urls = make_gallery_urls()
        
        # download all media
        local_urls = []
        i = 0
        for url in reddit_urls:
            i += 1
            name = f"temp/{post.id}/{i}"
            if self.debug: print(f"Downloading {url} ({i}/{len(reddit_urls)})")
            self.download_media(url, name)
            local_urls.append(name)
        
        return local_urls
    
    # uses reddit_download to get all posts' media in a list of posts
    # takes a list of posts, not a list of subs
    # returns a list of lists, one list per post containing the local download locations for that post
    def reddit_download_all(self, posts):
        image_locations = []
        for post in posts:
            image_locations.append(self.download(post))
        return image_locations


    ### WRAPPER METHODS; these should be the ones called directly
    # gets posts from a given service's place (ie, a subreddit or twitter feed)
    def scrape(self, place, limit=10):
        if self.debug: print(f"Scraping {self.service}: {place}... ")
        if self.service == "reddit":
            result = self.reddit_scrape(place, limit)
        if self.debug: print(f"Done scraping {self.service}: {place}.")
        return result
    # gets posts from a gives service's places (ie, multiple subreddits or feeds)
    def scrape_all(self, places=None, limit=10):
        if places == None: places = self.places
        if self.service == "reddit":
            result = self.reddit_scrape_all(places, limit)
        return result
    # downloads a given post's media and return the locations
    def download(self, post):
        if self.service == "reddit":
            if self.debug: print(f"Downloading {post.id}... ")
            result = self.reddit_download(post)
        if self.debug: print(f"Done downloading {post.id}.")
        return result
    # downloads a list of post's media and returns a list of the locations
    def download_all(self, posts):
        if self.service == "reddit":
            post_ids = [p.id for p in posts]
            result = self.reddit_download_all(posts)
        return result
    # creates the savefile for a list of posts.
    def remember(self, places=None, limit=10):
        if places == None: places = self.places
        if self.debug: print(f"Remembering {', '.join(places)}...")
        self.create_savefile(places, limit)
        if self.debug: print(f"Remembered {', '.join(places)}.")

    ### TOOTER METHODS (reddit only for now)
    # builds a toot for convenience
    def build_toot(self, masto, post):
        toot = {}
        toot["text"] = post.title
        if self.get_post_type(post) == "video": toot["text"] += f"\n\n{post.url}"
        local_media = self.download(post)
        toot["media"] = masto.upload_all_media(local_media)
        return toot
    # toots all posts in list
    def toot_posts(self, masto, posts):
        for post in posts:
            to_toot = self.build_toot(masto, post)
            masto.toot(to_toot["text"], to_toot["media"])
        return True
    
    ### RUNNING METHODS
    def run(self, masto, places=None, limit=10):
        if self.debug: print(f"Running {self.service}.")
        if places == None: places = self.places
        subs = self.scrape_all(places=places, limit=limit)
        for sub in subs:
            self.toot_posts(masto, subs[sub])
        self.remember()

def main():
    while True:
        # get config
        config = json.load(open('config.json', 'r'))
        # make bots
        masto = bot(config)
        reddit = scraper("reddit", config, debug=True)
        # run bots
        reddit.run(masto)
        # buffer time bc posts only happen so often
        time.sleep(60)
    
if __name__ == "__main__":
    main()
scrape_all