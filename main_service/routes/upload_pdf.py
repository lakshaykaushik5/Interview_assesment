from fastapi import UploadFile, APIRouter
from services import upload_pdf_service

upload_pdf_app = APIRouter()


@upload_pdf_app.post('/')
async def upload_pdf(file:UploadFile):
    return await upload_pdf_service(file)
    
    