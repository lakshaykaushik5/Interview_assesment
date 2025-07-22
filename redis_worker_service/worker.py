from redis import Redis,exceptions
from rq import Worker,Queue
import json
import time
import os
from ingestion import injestion
from dotenv import load_dotenv,find_dotenv
import asyncio

load_dotenv(find_dotenv())

redis_conn = Redis(host=os.getenv("REDIS_HOST"),port=os.getenv("REDIS_PORT"))
queue_name = os.getenv("QUEUE_NAME")

print(queue_name," ___________________")

async def process_message(json_message_string):
    print(". . .Job Recieved. . . ",json_message_string)
    try:
        job_data = json.loads(json_message_string)
        file_path = job_data.get('payload').get('path')
        doc_id = job_data.get('payload').get("id")
        print(doc_id," +++++++++++++++++++++++++++++++++++++",file_path)

        
        
        if not file_path or not doc_id:
            print("Error in redis worder file path or id not found")
            return
        
        if not os.path.exists(file_path):
            print(f"File not found on path {file_path}")
            return
        print("file found at path ",file_path)
        await injestion(file_path,doc_id) 
        return True
    except json.JSONDecodeError:
        print(f"Error Recieved non json message :{json_message_string}")
    except Exception as e:
        print(f"An Error Occured in process_message  ",e)            


async def listen_for_jobs():
    print(f"Worker Started .Listening on queue: {queue_name}")
    while True:
        try:
            message_tuple = redis_conn.blpop(queue_name,timeout=0)
            raw_message = message_tuple[1]
            
            await process_message(raw_message.decode("utf-8"))
            print(". . . .GOT THE JOB . . . .")
        except exceptions.ConnectionError as e:
            print(f"Connection Error : {e} . Retrying . . . . .")
            time.sleep(5)
        except Exception as e:
            print(f"Error in worker.py : {e}")
            

async def main():
    await listen_for_jobs()


if __name__ == "__main__":
    
    asyncio.run(main())