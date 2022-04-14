import requests
import os
import logging
from datetime import datetime

### HELPER METHODS
# helper method to clean out folder (delete all contents)
# expected structure: [["temp/a/1", "temp/a/2"], [], [], ["temp/e/1"]]
class helper():
    def __init__(service):
        # copy the service's variables to make them local
        # because it's easier to access and doesn't requre the
        # service to pass itself in every time
        service = service.service
        low_activity_random = service.low_activity_random
        places = service.places
        seent = service.seent

    def remove_folders(folders_list):
        for folder in folders_list:
            logging.info(f"Clearing folder {folder}")
            for file in folder:
                os.remove(file)
            if len(folder) > 0:
                subfolder = "/".join(folder[0].split("/")[:-1])
                os.rmdir(subfolder)

    # helper method to download media
    def download_media(url, filename):
        # get file first
        logging.info(f"Downloading {url} info {filename}")
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
    def get_post_type(post):
        if post.url[8] == 'i': return "image"
        if post.url[8] == 'v': return "video"
        if post.url[23:30] == "gallery": return "gallery"
        return "unknown"
    
    # returns True if the ts1 is older than ts2
    # tsx should be a timestamp value
    def ts_older(ts1, ts2):
        # timedelta of `hours`
        hours_delta = datetime.fromtimestamp(ts2) - datetime.fromtimestamp(0)
        # timedelta of timestamp
        stamp_delta = datetime.fromtimestamp(ts1)
        stamp_delta = datetime.now() - stamp_delta
        print("  ts_older: {stamp_delta} > {hours_delta}")
        return stamp_delta > hours_delta

    # returns True if place hasn't had a post in the past 12 hours according
    # to the savefile
    def been_awhile(seent_time, hours=12):
        long_time = 60 * 60 * hours
        return helper.ts_older(int(seent_time), long_time)
    
    # takes in a ListingGenerator (list of reddit posts) and 
    # reverses it
    def reddit_listify(LG):
        return [p for p in LG]
