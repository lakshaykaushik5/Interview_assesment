from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv, find_dotenv
import uvicorn

from langchain_core.messages import HumanMessage
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
import websockets
import base64

from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingParameters,
    StreamingEvents,
    BeginEvent,
    TurnEvent,
    TerminationEvent,
    StreamingError,
)

load_dotenv(find_dotenv())

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
voice_id = "21m00Tcm4TlvDq8ikWAM"

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = init_chat_model(
    model=os.getenv("MODEL_LLM_1"),
    api_key=os.getenv("MODEL_LLM_1_API_KEY"),
    streaming=True,
)

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
compile_graph = graph.compile()

async def stream_graph_updates_v1_1(input_queue: asyncio.Queue, output_queue: asyncio.Queue):
    try:
        while True:
            user_input = await input_queue.get()
            if user_input is None:
                break

            input_messages = [HumanMessage(content=user_input)]
            for chunk in llm.stream(input_messages):
                if hasattr(chunk, "content") and chunk.content:
                    print(chunk.content, end="", flush=True)
                    await output_queue.put(chunk.content)
            print()
    except Exception as e:
        print(f"Error in function stream_graph_updates_v1_1 :-: {e}")
    finally:
        # Signal end-of-stream exactly once when upstream ends
        await output_queue.put(None)

async def listen_fun(websocket: WebSocket, input_queue: asyncio.Queue):
    print("was here --------------- just few seconds ago ")
    try:
        while True:
            data = await websocket.receive_bytes()
            print(" ---------------1 ---------------")
            await input_queue.put(data)
    except WebSocketDisconnect:
        print("Websockets disconnected")
    except Exception as e:
        print(f" Error in listen_fun : - : {e}")
    finally:
        await input_queue.put(None)

async def send_fun(websocket: WebSocket, output_queue: asyncio.Queue):
    try:
        while True:
            send_data = await output_queue.get()
            if send_data is None:
                break
            if isinstance(send_data, (bytes, bytearray)):
                await websocket.send_bytes(send_data)
            elif isinstance(send_data, str):
                await websocket.send_text(send_data)
            else:
                await websocket.send_json(send_data)
    except WebSocketDisconnect:
        print("Websocket disconnected in send_fun")
    finally:
        pass

def create_event_handlers(output_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
    def on_begin(client: StreamingClient, event: BeginEvent):
        print(f"Session Started : {event.id}")

    def on_turn(client: StreamingClient, event: TurnEvent):
        print(f"Transcript update : {event.transcript}")
        asyncio.run_coroutine_threadsafe(output_queue.put(event.transcript), loop)

    def on_termination(client: StreamingClient, event: TerminationEvent):
        print(f"Session terminated after {event.audio_duration_seconds} seconds")

    def on_error(client: StreamingClient, error: StreamingError):
        print(f"Error :::::::::::::: {error}")

    return on_begin, on_turn, on_termination, on_error

assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
print(assemblyai_api_key, " ===================================== ")

async def speech_to_assemblyai(input_queue: asyncio.Queue, output_queue: asyncio.Queue):
    client = StreamingClient(
        StreamingClientOptions(
            api_key=assemblyai_api_key,
            api_host="streaming.assemblyai.com",
        )
    )
    loop = asyncio.get_running_loop()
    on_begin, on_turn, on_termination, on_error = create_event_handlers(output_queue, loop)

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_termination)
    client.on(StreamingEvents.Error, on_error)

    # Synchronous connect (do not await)
    client.connect(
        StreamingParameters(
            sample_rate=16000,
            format_turns=True,
        )
    )

    try:
        while True:
            data = await input_queue.get()
            if data is None:
                break
            # Offload sync stream() to a thread
            await loop.run_in_executor(None, client.stream, data)
    finally:
        client.disconnect(terminate=True)

async def send_json_to_11labs(task_queue: asyncio.Queue, output_queue: asyncio.Queue):
    # v2_5 is current; v2 also works. Adjust if needed.
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_turbo_v2"

    # Do not pass headers kwarg to avoid version-specific kwargs errors;
    # authenticate in the first message instead.
    async with websockets.connect(uri) as ws:
        # Initial priming message recommended: a single space " " and voice settings,
        # include xi_api_key here for auth.
        await ws.send(
            json.dumps(
                {
                    "text": " ",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
                    "xi_api_key": ELEVENLABS_API_KEY,
                }
            )
        )

        async def listen():
            while True:
                try:
                    message = await ws.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        audio_bytes = base64.b64decode(data["audio"])
                        await output_queue.put(audio_bytes)
                    if data.get("isFinal") or data.get("done"):
                        break
                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    print(f"11labs listen error: {e}")
                    break

        listen_task = asyncio.create_task(listen())

        while True:
            text = await task_queue.get()
            if text is None:
                # Force generation then end-of-stream
                await ws.send(json.dumps({"flush": True}))
                await ws.send(json.dumps({"text": ""}))
                break
            await ws.send(json.dumps({"text": text}))

        await listen_task

app = FastAPI()

@app.websocket("/ws")
async def langgraph_listen(websocket: WebSocket):
    await websocket.accept()
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    assemblyai_output_queue = asyncio.Queue()
    ll_labs_input_queue = asyncio.Queue()

    listen_task = asyncio.create_task(listen_fun(websocket, input_queue))
    assemblyai_task = asyncio.create_task(speech_to_assemblyai(input_queue, assemblyai_output_queue))
    graph_stream_task = asyncio.create_task(
        stream_graph_updates_v1_1(assemblyai_output_queue, ll_labs_input_queue)
    )
    elevenlabs_task = asyncio.create_task(send_json_to_11labs(ll_labs_input_queue, output_queue))
    send_task = asyncio.create_task(send_fun(websocket, output_queue))

    await asyncio.gather(
        listen_task, assemblyai_task, graph_stream_task, elevenlabs_task, send_task
    )

if __name__ == "__main__":
    print(" Starting Server at port 8000 . . . . .")
    uvicorn.run(app, host="localhost", port=8000)
