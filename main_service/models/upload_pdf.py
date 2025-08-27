from fastapi import UploadFile
from pydantic import BaseModel,HttpUrl


class ResumeData(BaseModel):
    file:UploadFile
    webhookurl:HttpUrl