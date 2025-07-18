from redis import Redis,exceptions
from rq import Worker,Queue
import json
import time
import os

redis_conn = Redis(host="localhost",port=6379)
queue_name = 'Resume'


def process_message(json_message_string):
    print(". . .Job Recieved. . . ",json_message_string)
    try:
        job_data = json.loads(json_message_string)
        print(job_data," +++++++++++++++++")
        file_path = job_data.get('payload').get('path')
        doc_id = job_data.get('payload').get("id")
        
        if not file_path or not doc_id:
            print("Error in redis worder file path or id not found")
            return
        
        if not os.path.exists(file_path):
            print(f"File not found on path {file_path}")
            return
        print("file found at path ",file_path)
        return True
    except json.JSONDecodeError:
        print(f"Error Recieved non json message :{json_message_string}")
    except Exception as e:
        print(f"An Error Occured in process_message  ",e)            


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