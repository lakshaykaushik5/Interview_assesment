import json
from sse_starlette import EventSourceResponse
import os
from dotenv import load_dotenv,find_dotenv
from utils import verify_webhook_signature
import requests
from fastapi import HTTPException,Request
from db import init_redis

load_dotenv(find_dotenv())


async def list_webhook(req:Request):
    "Recieve Webhooks from worker service"
    try:
        raw_data = await req.body()
        
        raw_payload_str = raw_data.decode('utf-8')
        
        signature = requests.headers.get('x-webhook-signature')
        
        if not signature:
            print("No Signature provided")
            raise HTTPException(status_code=401,detail="No Signature provided")

        check_signature = verify_webhook_signature(raw_payload_str,signature)
        
        if not check_signature:
            raise HTTPException(status_code=500,detail="Invalid Signature")
        
        
        webhook_data = json.loads(raw_payload_str)
        
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



