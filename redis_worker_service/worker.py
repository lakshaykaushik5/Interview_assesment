from redis import Redis,exceptions
from rq import Worker,Queue
import json
import time
import os
from ingestion import injestion
from dotenv import load_dotenv,find_dotenv
import asyncio
import hmac
import hashlib
from datetime import datetime
import requests

load_dotenv(find_dotenv())

redis_conn = Redis(host=os.getenv("REDIS_HOST"),port=os.getenv("REDIS_PORT"))
queue_name = os.getenv("QUEUE_NAME")

print(queue_name," ___________________")

webhook_secret = ""
def create_signature(payload:str):
    """Create HMAC Signature for authentication"""
    
    return f"sha256={hmac.new(webhook_secret.encode('uff-8'),payload.encode('utf-8'),hashlib.sha256).hexdigest()}"



def send_webhook(webhook_url:str,id:str):
    """Send webhook notification to frontend"""
    webhook_payload = {
        "jobId":id,
        "status":"completed",
        "timestamp":datetime.now().isoformat()
    }
    
    payload_json = json.dumps(webhook_payload)
    signature = create_signature(webhook_payload)
    
    headers = {
        "Content-Type":"application/json",
        "X-Webhook-Signature":signature,
        "User-Agent":"Worker/Service/1.0"
    }
    
    try:
        
        response = requests.post(
            webhook_url,
            data=payload_json,
            headers=headers,
            timeout=30
        )
        
        if response.status_code==200:
            print("-------------Webhook--sent--successfully------------------")
            return True
        else:
            print(f"-------------Error : {response.status.code}--------------")
            return False
    except exceptions as e:
        print(f"Error :-: {e}")
    
    print("------------done--------------")

async def process_message(json_message_string):
    print(". . .Job Recieved. . . ",json_message_string)
    try:
        job_data = json.loads(json_message_string)
        file_path = job_data.get('payload').get('path')
        doc_id = job_data.get('payload').get("id")
        webhook_url = job_data.get('payload').get('web_hook_url')
        print(doc_id," +++++++++++++++++++++++++++++++++++++",file_path,webhook_url)

        
        
        if not file_path or not doc_id:
            print("Error in redis worder file path or id not found")
            return
        
        if not os.path.exists(file_path):
            print(f"File not found on path {file_path}")
            return
        print("file found at path ",file_path)
        await injestion(file_path,doc_id) 
        send_webhook(webhook_url)
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