from fastapi import FastAPI, WebSocket,WebSocketDisconnect
import websockets
import asyncio

import json

app = FastAPI()

voice_id = ""
ELEVENLABS_API_KEY=""

async def send_audio_file_to_langgraph_service(audio_data):
    uri = "wss://localhost:4001/v1/listening_websocket"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "audio":audio_data
        }))


async def send_json_to_11labs(task_queue):
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_turbo_v2"
    
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "text":"",
            "voice_settings":{"stability":0.5,"similarity_boost":0.5},
            "xi_api_keys":ELEVENLABS_API_KEY
        }))
        
        
        async def listen():
            while True:
                try:
                    messages = await ws.recv()
                    data = json.loads(messages)
                    if data.get("audio"):
                        await send_audio_file_to_langgraph_service(data)
                    elif data.get("isFinal"):
                        break
                        
                except websockets.exceptions as e:
                    print(e)
                    
        listen_task = asyncio.create_task(listen())
        
        while True:
            text = await task_queue.get()
            if text is None:
                break
            await ws.send(json.dumps({"text":text}))
            await ws.send({"text":""})
        
        await listen_task        


@app.websocket("/ws")
async def tts_websocket(websocket:WebSocket):
    
    await websocket.accept()
    task_queue = asyncio.Queue()
    
    elevenlabs_task = asyncio.create_task(send_json_to_11labs(task_queue))

    try:
        while True:
            data = websocket.receive_json()
            text = data.get("text")
            await task_queue.put(text)
            # await websocket.send_bytes()
    except WebSocketDisconnect:
        pass
    finally:
        await task_queue.put(None)
        await elevenlabs_task 
        

    
    
    