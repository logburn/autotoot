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
    # get config
    config = json.load(open('config.json', 'r'))

    # get settings if applicable
    neuter = False
    wait = 5
    if "autotoot" in config:
        c = config["autotoot"]
        if "neuter" in c:
            neuter = c["neuter"].lower() == "true"
        if "wait" in c:
            wait = int(c["wait"])
    print(neuter, wait)
    # make bots
    masto = bot(config, neuter=neuter)
    reddit = scraper("reddit", config, neuter=neuter)

    # run bots forever
    while True:
        run(masto, reddit)
        time.sleep(wait)
    
if __name__ == "__main__":
    main()
