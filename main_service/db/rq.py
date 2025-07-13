from redis import Redis

from rq import Queue

redis_connection= Redis(
    host="redis",
    port="6379"
)

q = Queue(connection=Redis(redis_connection))