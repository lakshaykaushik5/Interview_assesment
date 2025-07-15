import os
import aiofiles
from db import redis_connection
import json

async def save_to_disk(file:bytes,path:str):
    try:
        os.makedirs(os.path.dirname(path),exist_ok=True)
    
        async with aiofiles.open(path,'wb') as out_file:
            await out_file .write(file)
            
        return True
    except Exception as e:
        print(f"Error in utils :-: ",e)
        return False
    

def enqueue_file(file_type:any,payload:any):
    try:
        message = json.dumps({
            "file_type":file_type,
            "payload":payload
        })
        
        redis_connection.rpush(file_type,message)
        return True
    except Exception as e:
        print(f" Error in enqueue_file ::-:: {e}")
        return False