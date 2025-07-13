from fastapi import FastAPI, APIRouter
from .upload_pdf import upload_pdf_app


router = APIRouter()


router.include_router(upload_pdf_app,prefix="/upload-pdf",tags=["Uploads_Pdf"])

