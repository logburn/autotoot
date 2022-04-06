# Autotoot
Autotoot is designed to take posts from a scraper (eg, Reddit) and post them on Mastodon. The scripts should be general purpose enough
that you can plug your own things in. For example, one could write their own scraper and plug in to the existing Mastodon bot. This repo
is very much a work in progress.

### Pip requirements:
    - Mastodon.py
    - praw
you can run `pip3 install Mastodon.py praw` to install both of these.

## Status:
**Done**
- [x] Download and posting of video files
- [x] Make sure text-only reddit posts work
- [x] Eternal looping, run script every 5 mins or something
- [x] Different masto post structures for different post types (videos need links)
- [x] Import bot/scraper settings from file for automation
- [x] Random post if low activity
- [x] Separate methods methods to make code cleaner
- [x] Keep track of what has been scraped and tooted to not duplicate posts

**Likely**
- [ ] Debugging logging
- [ ] Move all vars into config
- [ ] Docker image

**Unlikely**
- [ ] Updating from @mention toot
- [ ] Make this an installable (pip?) package
- [ ] Add twitter bot
