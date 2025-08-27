from fastapi import FastAPI ,APIRouter
from services import job_events,list_webhook


webhook_router = APIRouter()

@webhook_router.post('/list-webhook')
async def reciev_webhooks(webhook_data:dict):
    return await list_webhook(webhook_data)


@webhook_router.get('/job-event')
async def sse_job_event(jobId:str):
    return await job_events(jobId)
    