from fastapi import FastAPI ,APIRouter,Request
from services import job_events,list_webhook


webhook_router = APIRouter()

@webhook_router.post('/list-webhook')
async def reciev_webhooks(req:Request):
    return await list_webhook(req)


@webhook_router.post('/job-event')
async def sse_job_event(req:Request):
    body = await req.json()
    jobId = body.get('payload').get('data')
    return await job_events(jobId)
    