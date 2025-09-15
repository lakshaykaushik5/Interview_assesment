from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv, find_dotenv
import uvicorn

from langchain_core.messages import HumanMessage
from fastapi import FastAPI,WebSocket,WebSocketDisconnect
import asyncio
import json
import websockets
from assemblyai.streaming.v3 import (StreamingClient, StreamingClientOptions, StreamingParameters,StreamingEvents,BeginEvent,TurnEvent,TerminationEvent,StreamingError)
from typing import AsyncGenerator, Type

load_dotenv(find_dotenv())

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
voice_id = "21m00Tcm4TlvDq8ikWAM"





load_dotenv(find_dotenv())

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = init_chat_model(
    model=os.getenv("MODEL_LLM_1"),
    api_key=os.getenv("MODEL_LLM_1_API_KEY"),
    streaming=True  # Enable streaming mode in the LLM
)

# Updated chatbot function to yield token-by-token response
def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages":[response]}
    # `invoke` returns an async generator or iterator over tokens when streaming=True

graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

compile_graph = graph.compile()

async def stream_graph_updates_v1_1(input_queue,output_queue):
    while True:
        try:
            user_input = await input_queue.get()
            if user_input is None:
                break
            
            input_messages = [HumanMessage(content=user_input)]
            
            for chunk in llm.stream(input_messages):
                if hasattr(chunk,'content') and chunk.content:
                    print(chunk.content,end="",flush=True)
                    await output_queue.put(chunk.content)
            print()
        except Exception as e:
            print(f"Error in function stream_graph_updates_v1_1 :-:{e}")
        finally:
            await output_queue.put(None)


# async def stream_graph_updates_v1(input_queue,output_queue):
#     user_input = await input_queue.get()
#     messages = [HumanMessage(content=user_input)]
    
#     # Stream directly from LLM for token-by-token output
#     stream_msg = llm.stream(messages)
#     for chunk in stream_msg:
#         if hasattr(chunk, "content") and chunk.content:
#             print(chunk.content, end="", flush=True)
#             await output_queue.put(chunk.content)
#     print()  # Newline after complete response

# Option 2: Stream at the graph level (node-by-node)
# def stream_graph_updates_v2(user_input: str):
#     initial_state = {"messages": [HumanMessage(content=user_input)]}
    
#     for event in compile_graph.stream(initial_state):
#         for node_name, node_output in event.items():
#             if "messages" in node_output and node_output["messages"]:
#                 latest_message = node_output["messages"][-1]
#                 if hasattr(latest_message, "content"):
#                     print(f"Assistant: {latest_message.content}")

# Option 3: Using stream_mode="messages" (if you want message-level streaming)
# def stream_graph_updates_v3(user_input: str):
#     initial_state = {"messages": [HumanMessage(content=user_input)]}
    
#     for msg, metadata in compile_graph.stream(initial_state, stream_mode="messages"):
#         if hasattr(msg, "content") and msg.content:
#             print("Assistant:", msg.content)

# while True:
#     try:
#         user_input = input('User: ')
#         if user_input == "q":
#             break
        
#         # Choose one of the streaming options:
#         stream_graph_updates_v1(user_input)  # Token-by-token (fastest feedback)
#         # stream_graph_updates_v2(user_input)  # Node-by-node
#         # stream_graph_updates_v3(user_input)  # Message-level
        
#     except Exception as e:
#         print("Error:", e)
    

async def listen_fun(websocket,input_queue):
    print("was here --------------- ")
    try:
        while True:
            data = await websocket.receive_json()  
            print(" ---------------1 ---------------",data)
            await input_queue.put(data)
    except WebSocketDisconnect:
        print("Websockets disconnected")
    except Exception as e:
        print(f" Error in listen_fun : - : {e}")
    finally:
        await input_queue.put(None)

async def send_fun(websocket,output_queue):
    try:
        while True:
            send_data = await output_queue.get()
            if send_data is None:
                break
            await websocket.send(send_data)
    except WebSocketDisconnect:
        print(f"Websocket disconnected in send fun")
    finally:
        pass
    

def create_event_handlers(output_queue: asyncio.Queue,loop):
    def on_begin(client: Type[StreamingClient], event: BeginEvent):
        print(f"Session Started : {event.id}")

    def on_turn(client: Type[StreamingClient], event: TurnEvent):
        print(f"Transcript update : {event.transcript}")
        # Use create_task to avoid blocking
        asyncio.run_coroutine_threadsafe(output_queue.put(event.transcript),loop)

    def on_termination(client: Type[StreamingClient], event: TerminationEvent):
        print(f"Session terminated after {event.audio_duration_seconds} seconds")

    def on_error(client: Type[StreamingClient], error: StreamingError):
        print(f"Error : {error}")

    return on_begin, on_turn, on_termination, on_error

    


assemblyai_api_key = os.getenv('ASSEMBLYAI_API_KEY')



async def speech_to_assemblyai(input_queue,output_queue):
    client = StreamingClient(
        StreamingClientOptions(
            api_key=assemblyai_api_key,
            api_host = "streaming.assemblyai.com"
    ))
    loop = asyncio.get_running_loop()

    on_begin, on_turn, on_termination, on_error = create_event_handlers(output_queue,loop)

    
    client.on(StreamingEvents.Begin,on_begin)
    client.on(StreamingEvents.Turn,on_turn)
    client.on(StreamingEvents.Termination,on_termination)
    client.on(StreamingEvents.Error,on_error)
    
    client.connect(
        StreamingParameters(
            sample_rate=16000,
            format_turns=True
        )
    )
    
    try:
        while True:
            data = await input_queue.get()
            if data is None:
                break        
            await client.stream(data)
    finally:
        await client.disconnect(terminate = True)
        

async def send_json_to_11labs(task_queue,output_queue):
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
                        await output_queue.put(data)
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



app = FastAPI()

@app.websocket("/ws")
async def langgraph_listen(websocket:WebSocket):
    await websocket.accept()
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    assemblyai_output_queue = asyncio.Queue()
    langgraph_output_queue = asyncio.Queue()
    ll_labs_input_queue = asyncio.Queue()
    
    
    listen_task = asyncio.create_task(listen_fun(websocket,input_queue))
    assemblyai_task = asyncio.create_task(speech_to_assemblyai(input_queue,assemblyai_output_queue))
    # stream_graph_updates_v1
    graph_stream_task = asyncio.create_task(stream_graph_updates_v1_1(assemblyai_output_queue,ll_labs_input_queue))
    elevenlabs_task = asyncio.create_task(send_json_to_11labs(ll_labs_input_queue,output_queue))
    send_task = asyncio.create_task(send_fun(websocket,output_queue))
    
    
    await asyncio.gather(listen_task,assemblyai_task,graph_stream_task,elevenlabs_task,send_task)
    
    


if __name__=='__main__':
    print(" Starting Server at port 8000 . . . . .")
    uvicorn.run(app,host="localhost",port = 8000)