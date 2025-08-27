from fastapi import FastAPI, APIRouter
from .upload_pdf import upload_pdf_app
from .webhook import webhook_router

router = APIRouter()


router.include_router(upload_pdf_app,prefix="/upload-pdf",tags=["Uploads_Pdf"])

router.include_router(webhook_router,prefix="/webhook",tags=["webhook"])