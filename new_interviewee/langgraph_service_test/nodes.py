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

