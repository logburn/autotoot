from mastodon import Mastodon
import logging

# Mastodon bot to post things
class bot():
    def __init__(self, config, neuter=False):
        self.masto = Mastodon(access_token=config["mastodon"]["access_token"], api_base_url=config["mastodon"]["host"])
    
    # uploads media to mastodon, returns the mastodon ID
    # specify mimetype of video files as "video/mp4" to avoid error
    def upload_media(self, filename, mimetype=None):
        logging.info(f"Uploading media {filename}")
        return self.masto.media_post(filename, mime_type=mimetype)
    
    # uploads all given media
    def upload_all_media(self, filenames):
        ids = []
        for fn in filenames:
            if not self.neuter:
                ids.append(self.upload_media(fn))
            else:
                print(f"Would have uploaded {fn}")
        return ids
    
    def toot(self, text, media=None):
        logging.info(f"Posting:\n  Text: {text}")
        if not self.neuter:
            self.masto.status_post(text, media_ids=media)
        else:
            print(f"Would have tooted: {text}")
