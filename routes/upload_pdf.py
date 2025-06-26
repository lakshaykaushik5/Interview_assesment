from fastapi import FastAPI,UploadFile,APIRouter
from uuid import uuid4

upload_pdf_app = APIRouter()


@upload_pdf_app.post('/')
async def upload_pdf(file:UploadFile):
    
    file_path = f"/mnt/uploads/{id}/{file.filename}"
    pass