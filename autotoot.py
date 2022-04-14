from bot import bot
from scraper import scraper
import json
import time

def run(masto, service):
    # post any new posts, up to limit
    subs = service.scrape_all()
    for sub in subs:
        service.toot_posts(masto, subs[sub])
    service.remember()

    # post random if it has been a while
    service.keep_lively()

def main():
    while True:
        # get config
        config = json.load(open('config.json', 'r'))
        # make bots
        masto = bot(config, neuter=True)
        reddit = scraper("reddit", config, neuter=True)
        # run bots
        run(masto, reddit)
        # buffer time bc posts only happen so often so why check
        time.sleep(5)
    
if __name__ == "__main__":
    main()
