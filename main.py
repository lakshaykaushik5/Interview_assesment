from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
def test():
    return {"msg":"success"}


if __name__=='__main__':
    uvicorn.run(app,host="localhost",port = 4001)