import asyncio
import websockets
import shutil
import json
import base64
import os
import subprocess
from openai import AsyncOpenAI
from dotenv import load_dotenv,find_dotenv


load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv('MODEL_LLM_1_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
VOICEID = "21m00Tcm4TlvDq8ikWAM"


aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

def is_installed(lib_name):
    return shutil.which(lib_name) is not None


async def text_chunker(chunks):
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ''
    
    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer + ""
            buffer = text
        # elif text.startswith(splitters):
        #     yield buffer + text[0] + " "
        #     buffer = text[1:]
        else:
            buffer += text
    
    if buffer:
        yield buffer
        

async def stream(audio_stream):
    if not is_installed("mpv"):
        print("mpv not installed")
        return 
    
    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    
    print("Started streaming audio")
    
    async for chunk in audio_stream:
        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()
        
    
    if mpv_process.stdin:
        mpv_process.stdin.close()
    
    mpv_process.wait()
    

async def text_to_speech_input_streaming(voice_id,text_iterator):
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_turbo_v2"

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "text":" ",
            "voice_settings":{"stability":0.5,"similarity_boost":0.8},
            "xi_api_key":ELEVENLABS_API_KEY
        }))
        
        
        async def listen():
            while True:
                try:
                    messages = await ws.recv()
                    data = json.loads(messages)
                    
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get("isFinal"):
                        break
                except websockets.exceptions.ConnectionClosed as e:
                    print(e)
                    break   
            
        listen_task = asyncio.create_task(stream(listen()))
        
        async for text in text_chunker(text_iterator):
            await ws.send(json.dumps({"text":text,"try_trigger_generation":True}))
        
        await ws.send(json.dumps({"text":""}))
            
        await listen_task


async def chat_completion(query):
    response = await aclient.chat.completions.create(model="gpt-4",messages=[{"role":'user','content':query}],temperature=1,stream=True)
    
    async def text_iterator():
        async for chunk in response:
            delta = chunk.choices[0].delta
            yield delta.content
    
    await text_to_speech_input_streaming(VOICEID,text_iterator())

if __name__ == "__main__":
    text_to_send = "hello world"
    asyncio.run(chat_completion(text_to_send))