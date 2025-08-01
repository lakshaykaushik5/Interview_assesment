from fastapi import FastAPI
import uvicorn
from routes import router
from contextlib import asynccontextmanager
from db import init_db, engine


@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application Startup ::: Initializing Database............")
    await init_db()
    print("Database Initialized.")
    
    yield
    
    print("Application ShutDown ::: Disposing Database engine...........")
    await engine.dispose()
    print("Database engine disposed.")
    
    

app = FastAPI(lifespan=lifespan)

@app.get('/')
def test():
    return {"msg":"success"}


app.include_router(router,prefix="/v1",tags=["v1"])

if __name__=='__main__':
    uvicorn.run(app,host="localhost",port = 4001)