import os
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_client = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(redis_client):
        worker = Worker(map(Queue, listen))
        worker.work()