import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import grpc
from generated import audio_pb2, audio_pb2_grpc

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def audio_chunk_generator(websocket: WebSocket):
    try:
        while True:
            data = await websocket.receive_bytes()
            # Call time.time() properly to get current timestamp as int milliseconds
            chunk = audio_pb2.AudioChunk(audio_data=data, timestamp=int(time.time() * 1000))
            yield chunk
    except WebSocketDisconnect:
        # Client disconnected, stop generator
        return


@app.websocket("/ws")
async def websocket_audio_sender(websocket: WebSocket):
    print("WebSocket connection attempt")
    await websocket.accept()
    print("Accepted connection")

    async with grpc.aio.insecure_channel("localhost:50061") as channel:
        audio_stub = audio_pb2_grpc.SpeechToTextStub(channel)

        try:
            # Properly call the Transcribe RPC with the async generator
            call = audio_stub.Transcribe(audio_chunk_generator(websocket))

            async for confirmation in call:
                # confirmation.received is a bool, send it as string for WebSocket text
                await websocket.send_text(str(confirmation.received))

        except Exception as e:
            print(f"gRPC stream error: {e}")
            await websocket.close(code=1011, reason="gRPC stream error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8010)
