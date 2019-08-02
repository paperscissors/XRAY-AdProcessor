#!/usr/bin/python3
import os

import redis
from rq import Worker, Queue, Connection

import sentry_sdk
from sentry_sdk.integrations.rq import RqIntegration

from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
 
sentry_sdk.init(os.getenv("SENTRY_DSN"), integrations=[RqIntegration()])

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
