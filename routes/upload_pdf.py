from fastapi import FastAPI,UploadFile
from uuid import uuid4

app = FastAPI()


@app.post('/')
async def upload_pdf(file:UploadFile):
    
    file_path = f"/mnt/uploads/{id}/{file.filename}"
    pass