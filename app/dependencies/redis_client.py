import json
import os
from datetime import timedelta

import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0
)



def get_redis_key():
    return "hex_data"


def set_redis_data(data):
    key = get_redis_key()
    redis_client.set(key, json.dumps(data))
    redis_client.expire(key, timedelta(days=1))


def get_redis_data():
    key = get_redis_key()
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None
