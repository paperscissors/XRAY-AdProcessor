from AdProcessor import AdProcessor
from urllib import request, parse
import json
import os

from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def run_process(episode_id, preroll_id, postroll_id):
    # we need to query the database for matching ids to get the URIs for these assets

    try:
        process = AdProcessor("beervana.mp3", "one.mp3", "two.mp3") # postroll is totally optional
    except Exception as e:
        notify('Ads server failed: ' + str(e))

    notify('Ads server was successful '+episode_id)

    # send notification to slack
def notify(message):
    post = {"text": "{0}".format(message)}

    try:
        json_data = json.dumps(post)
        req = request.Request(os.getenv("SLACK_URL"),
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'})
        resp = request.urlopen(req)
    except Exception as em:
        print("EXCEPTION: " + str(em))
