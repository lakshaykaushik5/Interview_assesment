import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import grpc
from generated import audio_pb2,audio_pb2_grpc
import time



app = FastAPI()


async def audio_chunk_generator(websocket:WebSocket):
    try:
        while True:
            data = await websocket.receive_bytes()
            chunk =  audio_pb2.AudioChunk(audio_data = data,timestamp=time.time)
            yield chunk
    except WebSocketDisconnect:
        return


@app.websocket("/ws/audio")
async def websocket_audio_sender(websocket):
    
    await websocket.accept()
    
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        audio_channel = audio_pb2_grpc.SpeechToTextStub(channel)
        
        async def audio_gen():
            async for chunk in audio_chunk_generator(websocket):
                yield chunk
        
        try:
            call = audio_channel(audio_gen())
            async for confirmation in call:
                await websocket.send_text(confirmation.received)
        except Exception as e:
            await websocket.close(code=1011,reason="gRPC stream error ")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8010)
