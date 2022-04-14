from mastodon import Mastodon
import logging

# Mastodon bot to post things
class bot():
    def __init__(self, config, neuter=False):
        self.neuter = neuter
        self.masto = Mastodon(access_token=config["mastodon"]["access_token"], api_base_url=config["mastodon"]["host"])
    
    # uploads media to mastodon, returns the mastodon ID
    # specify mimetype of video files as "video/mp4" to avoid error
    def upload_media(self, filename, mimetype=None):
        logging.info(f"Uploading media {filename}")
        if not self.neuter:
            returnval = self.masto.media_post(filename, mime_type=mimetype)
        else:
            print(f"Would have uploaded {filename}")
            returnval = True
        return returnval
    
    # uploads all given media
    def upload_all_media(self, filenames):
        ids = []
        for fn in filenames:
            ids.append(self.upload_media(fn))
        return ids
    
    def toot(self, text, media=None):
        logging.info(f"Posting:\n  Text: {text}")
        if not self.neuter:
            self.masto.status_post(text, media_ids=media)
        else:
            print(f"Would have posted {text}")
