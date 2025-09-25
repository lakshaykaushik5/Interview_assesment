from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from concurrent import futures
import websockets
import asyncio
import assemblyai as aai
import asyncio
import json
from typing import AsyncGenerator, Type
from dotenv import load_dotenv,find_dotenv
import grpc


from assemblyai.streaming.v3 import (StreamingClient, StreamingClientOptions, StreamingParameters,StreamingEvents,BeginEvent,TurnEvent,TerminationEvent,StreamingError)


import os

from .generated import audio_pb2,audio_pb2_grpc

load_dotenv(find_dotenv())




assemblyai_api_key = os.getenv('ASSEMBLYAI_API_KEY')


# app = FastAPI()

def create_event_handlers():
    def on_begin(client: Type[StreamingClient], event: BeginEvent):
        print(f"Session Started : {event.id}")

    def on_turn(client: Type[StreamingClient], event: TurnEvent):
        print(f"Transcript update : {event.transcript}")
        # Use create_task to avoid blocking
        # asyncio.create_task(output_queue.put(event.transcript))/

    def on_termination(client: Type[StreamingClient], event: TerminationEvent):
        print(f"Session terminated after {event.audio_duration_seconds} seconds")

    def on_error(client: Type[StreamingClient], error: StreamingError):
        print(f"Error : {error}")

    return on_begin, on_turn, on_termination, on_error

    



async def speech_to_assemblyai(audio_data):
    client = StreamingClient(
        api_key=assemblyai_api_key,
        api_host = "streaming.assemblyai.com"
    )
    
    on_begin, on_turn, on_termination, on_error = create_event_handlers()

    
    client.on(StreamingEvents.Begin,on_begin)
    client.on(StreamingEvents.Turn,on_turn)
    client.on(StreamingEvents.Termination,on_termination)
    client.on(StreamingEvents.Error,on_error)
    
    await client.connect(
        StreamingParameters(
            sample_rate=16000,
            format_turns=True
        )
    )
    
    try:
        while True:
            data = audio_data
            if data is None:
                break        
            await client.stream(data)
    finally:
        await client.disconnect(terminate = True)
        


# async def receive_chunk(websocket,input_queue):
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             await input_queue.put(data)
#     except WebSocketDisconnect:
#         await input_queue.put(None)
        


# async def send_transcripts(websocket,output_queue):
#     try:
#         while True:
#             transcripts = await output_queue.get()
#             if transcripts is None:
#                 break
#             await websocket.send_json({"transcripts":transcripts})
#     except WebSocketDisconnect:
#         print(f"WebSocket Disconnected")



# @app.websocket("/ws")
# async def speech_to_text(websocket:WebSocket):
#     await websocket.accept()
    
#     input_queue = asyncio.Queue()
#     output_queue = asyncio.Queue()
    
#     listen_task = asyncio.create_task(receive_chunk(websocket,input_queue))
#     assemblyai_task = asyncio.create_task(speech_to_assemblyai(input_queue,output_queue))
#     send_task = asyncio.create_task(send_transcripts(websocket,output_queue))
    
    # await asyncio.gather(listen_task, assemblyai_task, send_task)
    
async def Transcribe(request_iterator,context):
    for request in request_iterator:
        print("request_made")
        
        # request_data = audio_pb2.AudioChunk()
        audio_data = request.audio_data
        timestamp = request.timestamp
        
        await speech_to_assemblyai(audio_data)
        
        reply = audio_pb2.ConfirmationMsg()
        reply.received=True
        
        yield reply
        
    

async def main_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_pb2_grpc.add_SpeechToTextServicer_to_server(speech_to_assemblyai(),server)
    server.add_insecure_port("localhost:50061")
    server.start()
    server.wait_for_termination()
    


if __name__ == "__main__":
    asyncio.run(main_server)