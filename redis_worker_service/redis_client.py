import os
import redis.asyncio as redis

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

global_redis = None



async def init_redis():
    global global_redis
    if global_redis is None:
        global_redis = await redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    return global_redis
