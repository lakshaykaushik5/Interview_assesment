from fastapi import FastAPI, APIRouter
from .upload_pdf import upload_pdf_app


router = FastAPI()


router.include_router(upload_pdf_app,prefix="/upload-pdf",tags=["Uploads_Pdf"])

