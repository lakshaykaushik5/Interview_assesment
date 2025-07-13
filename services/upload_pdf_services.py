import os
from fastapi import HTTPException,UploadFile,status
from fastapi.responses import JSONResponse
from db import get_session, MasterDocs
from utils import save_to_disk


async def upload_pdf_service(file:UploadFile):
    try:
        if not file:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="File not found")
        
        file_name = file.filename
        id = None
        async with get_session() as session:
            new_doc = MasterDocs(
                path=file_name
            )
            
            session.add(new_doc)
            await session.commit()
            await session.refresh(new_doc)
            id = new_doc.id
        
        if id ==None:
            HTTPException(status_code=404,detail="File Name Not Found")
        
        upload_dir = os.path.join(os.getcwd(), "uploads", str(id))
        file_path = os.path.join(upload_dir, file.filename)

        await save_to_disk(file=await file.read() ,path=file_path)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= str(id)
        )
        
        
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Internal Server Error :-: {e}")