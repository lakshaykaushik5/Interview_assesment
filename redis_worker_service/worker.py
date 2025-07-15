from redis import Redis,exceptions
from rq import Worker,Queue
import json
import time

redis_conn = Redis(host="localhost",port=6379)
queue_name = 'Resume'


def process_message(json_message_string):
    print(f"|-----| ",json_message_string)


def listen_for_jobs():
    print(f"Worker Started .Listening on queue: {queue_name}")
    while True:
        try:
            message_tuple = redis_conn.blpop(queue_name,timeout=0)
            raw_message = message_tuple[1]
            process_message(raw_message.decode("utf-8"))
        except exceptions.ConnectionError as e:
            print(f"Connection Error : {e} . Retrying . . . . .")
            time.sleep(5)
        except Exception as e:
            print(f"Error in worker.py : {e}")
            

if __name__ == "__main__":
    listen_for_jobs()