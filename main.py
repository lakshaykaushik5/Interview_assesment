from fastapi import FastAPI
import uvicorn
from routes import router

app = FastAPI()

@app.get('/')
def test():
    return {"msg":"success"}


app.include_router(router,prefix="/v1",tags=["v1"])

if __name__=='__main__':
    uvicorn.run(app,host="localhost",port = 4001)