import os
from dotenv import load_dotenv,find_dotenv
import websockets
import json
import asyncio
import base64

load_dotenv(find_dotenv())

ELEVEN_LABS_API_KEY=os.getenv("ELEVENLABS_API_KEY")

# print(ELEVEN_LABS_API_KEY,'-----------')

voice_id = "21m00Tcm4TlvDq8ikWAM"

model_id = 'eleven_flash_v2.5'

async def text_to_speech_ws_streaming(voice_id,model_id):
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "text":"",
            "voice_settings":{"stability":0.5,"similarity_boost":0.8,"use_speaker_boost":False},
            "generation_config":{
                "chunk_length_schedule":[120,160,250,290]
            },
            "xi_api_key":ELEVEN_LABS_API_KEY
        }))
        
        text = "Hi my name is IA1. How can i help you today"
        await websocket.send(json.dumps({"text":text}))
        await websocket.send(json.dumps({"text":""}))
        

async def write_to_local(audio_stream):
    with open(f'./output/test.mp3','wb') as f:
        async for chunk in audio_stream:
            if chunk:
                f.write(chunk)
                
                
                
                
                
async def listen(websocket):
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get('audio'):
                yield base64.b64decode(data["audio"])
            elif data.get('isFinal'):
                break
            
            
        except websockets.exceptions.ConnectionClosed as e:
            print(e)
            break
        
import requests

def check_subscription_and_voices():
    headers = {"xi-api-key": ELEVEN_LABS_API_KEY}
    
    # Check available voices
    voices_response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
    if voices_response.status_code == 200:
        voices = voices_response.json()
        for voice in voices["voices"]:
            if voice["voice_id"] == "Xb7hH8MSUJpSbSDYk0k2":
                print(f"Voice found: {voice['name']}")
                print(f"Category: {voice.get('category', 'N/A')}")
                break
    
    # Check subscription
    user_response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers)
    if user_response.status_code == 200:
        user_info = user_response.json()
        print(f"Subscription: {user_info.get('subscription', {}).get('tier', 'N/A')}")
    
    return voices_response.status_code, user_response.status_code

check_subscription_and_voices()


# asyncio.run(text_to_speech_ws_streaming(voice_id, model_id))
