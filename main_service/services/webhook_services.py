import aioredis
import json
from sse_starlette import EventSourceResponse
import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())


global_redis = None



async def init_redis():
    global global_redis
    if global_redis is None:
        global_redis = await aioredis.from_url("redis://localhost:6379", decode_responses=True)
    return global_redis


async def list_webhook(webhook_data:dict):
    "Recieve Webhooks from worker service"
    try:
        job_id=webhook_data.get("jobId")
        if not job_id:
            return {"success":False,"error":"Missing Job Id"}
        
        redis = await init_redis()
        await redis.publish(f"job:{job_id}",json.dumps(webhook_data))
        await redis.set(f"jobKey:{job_id}",json.dumps(webhook_data))
        
        return {"success":True}
    except Exception as e:
        return {"success":False,"error":str(e)}

async def job_events(jobId:str):
    """SSE endpoints"""
    
    async def event_generator():
        redis = await init_redis()
        
        pubsub = redis.pubsub()
        check_if_already_present = await redis.get(f"jobKey:{jobId}")
        
        if check_if_already_present:
            data = json.loads(check_if_already_present)
            yield {"event":"job_update","data":json.dumps(data)}

        await pubsub.subscribe(f"job:{jobId}")
            
        try:
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    data = json.loads(msg["data"])
                    yield {"event":"job_update","data":json.dumps(data)}
                        
                    if data.get('status') in ["completed","failed"]:
                        break
        finally:
            await pubsub.unsubscribe(f"job:{jobId}")
            await pubsub.close()
    return EventSourceResponse(event_generator())



# from typing import Dict,Set
# import redis
# from datetime import datetime,timedelta
# import json
# from sse_starlette.sse import EventSourceResponse
# import asyncio


# active_connection:Dict[str,asyncio.Queue]={}


# async def list_webhook(webhook_data:dict):
#     "recieve webhook from worker"
#     try:
#         job_id=webhook_data.get('jobId')
#         job_status = webhook_data.get('status')
#         job_timestamp = webhook_data.get('timestamp')

#         if job_id in active_connection:
#             try:
#                 await active_connection[job_id].put(json.dumps(webhook_data))
                
#             except:
#                 del active_connection[job_id]
        
#         return {'success':True}
        
#     except Exception as e:
#         return
    

# async def job_events(jobId:str):
#     """SSE endpoints for specific job updates"""
    
#     async def event_generator():
#         # active_connection[jobId] = True
#         queue = asyncio.Queue()
#         active_connection[jobId] = queue
        
#         try:
#             while True:
#                 message = await queue.get()
#                 yield {"event":"job_update","data":message}
                
#                 data = json.loads(message)
                
#                 if data.get("status") in ["completed","failed"]:
#                     break  
#         except Exception as e:
#             return e              
#         finally:
#             active_connection.pop(jobId,None)
    
#     return EventSourceResponse(event_generator())
                

