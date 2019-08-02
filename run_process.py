from AdProcessor import AdProcessor
import boto3
from urllib import request, parse
import json
import os
from pathlib import Path
import pymysql.cursors
import uuid

from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def run_process(episode_id, preroll_id, postroll_id=False):
    os.chdir(os.path.dirname(__file__))

    # we need to query the database for matching ids to get the URIs for these assets
    stream_uri = False
    preroll_uri = False
    postroll_uri = False

    working_directory = str(uuid.uuid4())

    os.mkdir(working_directory)

    db_user = os.getenv("DATABASE_USER")
    db_password = os.getenv("DATABASE_PASSWORD")
    db_name = os.getenv("DATABASE")
    db_host = os.getenv('DATABASE_HOST')

    connection = pymysql.connect(db_host,db_user,db_password,db_name)
    # query ids

    try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT stream_url from episodes WHERE id=%s", episode_id)

        stream_uri = cursor.fetchone()

    with connection.cursor() as cursor:
        cursor.execute("SELECT uri from ad_spots WHERE id=%s", preroll_id)

        preroll_uri = cursor.fetchone()

    if postroll_id:
        with connection.cursor() as cursor:
            cursor.execute("SELECT uri from ad_spots WHERE id=%s", postroll_id          )

            postroll_uri = cursor.fetchone()

    finally:
        connection.close()

    # download source files
    process_dir = os.getcwd()+'process/'

    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id='ACCESS_KEY',
                            aws_secret_access_key='SECRET_KEY')
    if stream_uri:
        stream_file = process_dir+working_directory+'episode.mp3'
        s3.download_file('xraystreaming', stream_uri, stream_file)

    if preroll_uri:
        preroll_file = process_dir+working_directory+'preroll.mp3'
        s3.download_file('xraystreaming', preroll_uri, preroll_file)

    if preroll_uri:
        preroll_file = process_dir+working_directory+'postroll.mp3'
        s3.download_file('xraystreaming', postroll_uri, preroll_file)
    # process

    # save filename + IDs to ad episode table
    check = Path(stream_file)
    if not check.is_file():
        stream_file = False

    check = Path(preroll_file)
    if not check.is_file():
        preroll_file = False

    check = Path(postroll_file)
    if not check.is_file():
        postroll_file = False

    try:
        final_filename = 'episode-'+str(uuid.uuid4())+'.mp3'
        process = AdProcessor(stream_file, preroll_file, postroll_file, final_filename)
        # when process is complete, upload to spaces again
        # clean up files
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
