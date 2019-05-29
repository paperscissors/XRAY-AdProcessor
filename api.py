from flask import Flask, abort

from rq import Queue
from rq.job import Job

from daemon import conn
import time
import logging
from run_process import run_process
import json

app = Flask(__name__)

q = Queue(connection=conn,default_timeout=3600)

@app.route("/<episode_id>/<preroll_id>/<postroll_id>")
def hey(episode_id, preroll_id, postroll_id):

    job = q.enqueue_call(
        func=run_process, args=(episode_id, preroll_id, postroll_id), kwargs={}, timeout=3600, result_ttl=5000
    )

    return json.dumps({'success':True, 'message':'Job queued.'}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    app.run(debug=False)
