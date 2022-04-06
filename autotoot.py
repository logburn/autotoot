from bot import bot
from scraper import scraper
import json
import time

'''
TODO:
    done:
      - [x] Download and posting of video files
      - [x] Make sure text-only reddit posts work
      - [x] Eternal looping, run script every 5 mins or something
      - [x] Different masto post structures for different post types (videos need links)
      - [x] Import bot/scraper settings from file for automation
      - [x] Random post if low activity
      
    likely:
      - […] Keep track of what has been scraped and tooted to not duplicate posts
      - […] Separate methdos methods to make code cleaner
      - […] Debugging logging
      - [ ] Move all vars into config
      - [ ] Docker image

    unlikely:
      - [ ] Updating from @mention toot
      - [ ] Make this an installable (pip?) package
      - [ ] Add twitter bot
'''

def run(masto, service):
    # post any new posts, up to limit
    print("Scraping")
    subs = service.scrape_all()
    print("Tooting if necessary")
    for sub in subs:
        print(f"  Tooting {sub}")
        service.toot_posts(masto, subs[sub])
    print("Remembering")
    service.remember()

    # post random if it has been a while
    print("Keeping lively")
    service.keep_lively()

def main():
    while True:
        # get config
        config = json.load(open('config.json', 'r'))
        # make bots
        masto = bot(config)
        reddit = scraper("reddit", config, low_activity_random=True)
        # run bots
        run(masto, reddit)
        # buffer time bc posts only happen so often so why check
        time.sleep(5)
    
if __name__ == "__main__":
    main()
