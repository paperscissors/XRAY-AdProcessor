from AdProcessor import AdProcessor
import boto3
from urllib import request, parse
import json
import os
from pathlib import Path
import pymysql.cursors
import shutil
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
    process_dir = os.getcwd()+'/process/'
    working_directory = str(uuid.uuid4())+"/"

    os.mkdir(process_dir+working_directory)

    db_user = os.getenv("DATABASE_USER")
    db_password = os.getenv("DATABASE_PASSWORD")
    db_name = os.getenv("DATABASE")
    db_host = os.getenv('DATABASE_HOST')

    connection = pymysql.connect(db_host,db_user,db_password,db_name, ssl={"fake_flag_to_enable_tls":True})
    # query ids

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT stream_url, name, podcast_id from episodes WHERE id=%s", episode_id)

            stream_uri = cursor.fetchone()

        with connection.cursor() as cursor:
            cursor.execute("SELECT uri, name from ad_spots WHERE id=%s", preroll_id)

            preroll_uri = cursor.fetchone()

        if postroll_id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT uri, name from ad_spots WHERE id=%s", postroll_id          )

                postroll_uri = cursor.fetchone()
    finally:
        connection.close()

    description = 'episode "' + stream_uri[1] + '"'

    try:
        description += ", preroll: "+preroll_uri[1]
    except NameError:
        print("preroll_uri not set")

    try:
        description += ", postroll: "+postroll_uri[1]
    except NameError:
        print("postroll_uri not set")

    # download source files
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=os.getenv('SPACES_REGION'),
                            endpoint_url=os.getenv('SPACES_ENDPOINT'),
                            aws_access_key_id=os.getenv('SPACES_ACCESS_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))
    if stream_uri:
        stream_file = process_dir+working_directory+'episode.mp3'
        client.download_file('xraystreaming', stream_uri[0], stream_file)

    if preroll_uri:
        preroll_file = process_dir+working_directory+'preroll.mp3'
        client.download_file('xraystreaming', preroll_uri[0], preroll_file)

    if postroll_uri:
        postroll_file = process_dir+working_directory+'postroll.mp3'
        client.download_file('xraystreaming', postroll_uri[0], postroll_file)

    # process
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
        uploaded_uri = 'podcasts/'+str(stream_uri[2])+'/'+str(episode_id)+'/processed/'+final_filename
        # when process is complete, upload to spaces again
        client.upload_file(os.getcwd()+'/results/'+final_filename,  # Path to local file
                   'xraystreaming',  # Name of Space
                   uploaded_uri)  # Name for remote file

        client.put_object_acl( ACL='public-read', Bucket='xraystreaming', Key=uploaded_uri )

        # save filename + IDs to ad episode table
        connection = pymysql.connect(db_host,db_user,db_password,db_name, ssl={"fake_flag_to_enable_tls":True})

        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO `episodes_with_ads` (`podcast_id`, `episode_id`, `preroll_id`, `postroll_id`, `uri`) VALUES (%s,%s,%s,%s,%s)", (str(stream_uri[2]), str(episode_id), str(preroll_id), postroll_id, uploaded_uri))

            connection.commit()

        finally:
            connection.close()

        # clean up files
        try:
           shutil.rmtree(process_dir+working_directory)
        except:
           print('Error while deleting directory')

    except Exception as e:
        notify('Ads server failed: ' + description + ': ' +  str(e))

    notify('Ads server successfully processed '+description + "\n https://xraystreaming.sfo2.digitaloceanspaces.com/"+uploaded_uri)


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
