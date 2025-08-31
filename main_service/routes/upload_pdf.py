from fastapi import UploadFile, APIRouter, Form, File
from services import upload_pdf_service
from models import ResumeData

upload_pdf_app = APIRouter()


@upload_pdf_app.post('/')
async def upload_pdf(file:UploadFile = File(...),webhookurl:str=Form(...)):
    print(" ------------------- Here --------------------")
    return await upload_pdf_service(file,webhookurl)
    
    