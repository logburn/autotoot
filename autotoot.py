from bot import bot
from scraper import scraper
import json
import time

def run(masto, service):
    # post any new posts, up to limit
    print("a")
    subs = service.scrape_all()
    print("b")
    i = 0
    for sub in subs:
        i += 1
        print(f"c{i}")
        service.toot_posts(masto, subs[sub])
        print("d")
    print("e")
    service.remember()
    print("f")

    # post random if it has been a while
    service.keep_lively()
    print("g")

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

    # make bots
    masto = bot(config, neuter=neuter)
    reddit = scraper("reddit", config, neuter=neuter)

    # run bots forever
    while True:
        run(masto, reddit)
        time.sleep(wait)
    
if __name__ == "__main__":
    main()
