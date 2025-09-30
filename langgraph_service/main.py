from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv, find_dotenv

from langchain_core.messages import HumanMessage
import asyncio
import grpc

from generated import llm_response_pb2,llm_response_pb2_grpc

load_dotenv(find_dotenv())


class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = init_chat_model(
    model=os.getenv("MODEL_LLM_1"),
    api_key=os.getenv("MODEL_LLM_1_API_KEY"),
    streaming=True,
)

async def chatbot(state: State):
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
compile_graph = graph.compile()

async def stream_graph_updates_v1_1(data):
    try:
        buffer_output = ""
        input_messages = [HumanMessage(content=data)]
        async for chunk in llm.stream(input_messages):
            if hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)
                buffer_output += chunk.content
                if any(buffer_output.endswith(p) for p in [".","!","?","\n"]) or len(buffer_output)>50:
                    
                    yield buffer_output
                    buffer_output = ""
        
        if buffer_output:
            yield buffer_output
            
        print()
    except Exception as e:
        print(f"Error in function stream_graph_updates_v1_1 :-: {e}")


class TranscriptsToLlmOperation(llm_response_pb2_grpc.TranscriptsToLlmServicer):
    
    async def llmOutput(self, request_iterator,context):
        
        async for request in request_iterator:
            print("====== Input Transcripts Received ======")
            # reply = await llm_response_pb2.OutputResponse(stream_graph_updates_v1_1(request.input_transcripts))
            # yield reply
            
            async for chunk in stream_graph_updates_v1_1(request.input_transcripts):
                yield llm_response_pb2.OutputResponse(output_response=chunk)
            
            

async def main():
    server = grpc.aio.server()
    llm_response_pb2_grpc.add_TranscriptsToLlmServicer_to_server(TranscriptsToLlmOperation(),server)
    
    server.add_insecure_port("[::]:50071")
    await server.start()
    print("gRPC server started at port ::::::::::::: 50071")
    await server.wait_for_termination()
    

if __name__ == "__main__":
    asyncio.run(main())