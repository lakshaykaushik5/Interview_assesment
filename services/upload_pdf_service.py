from fastapi import HTTPException



async def updload_pdf_service(file:bytes):
    try:
        file_path = f"/mnt/uploads/{id}/{file.filename}"
    except Exception as e:
        raise HTTPException(status_code=500,detail="Internal Server Error")