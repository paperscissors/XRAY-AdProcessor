#!/usr/bin/python
import os

import redis
from rq import Worker, Queue, Connection

import sentry_sdk
from sentry_sdk.integrations.rq import RqIntegration

sentry_sdk.init("https://a25edf001843418280ff13b0ee3ce61a@sentry.io/1471037", integrations=[RqIntegration()])

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
