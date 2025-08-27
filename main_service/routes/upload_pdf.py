from fastapi import UploadFile, APIRouter
from services import upload_pdf_service
from models import ResumeData

upload_pdf_app = APIRouter()


@upload_pdf_app.post('/')
async def upload_pdf(resume_data:ResumeData):
    print(" ------------------- Here --------------------")
    return await upload_pdf_service(resume_data)
    
    