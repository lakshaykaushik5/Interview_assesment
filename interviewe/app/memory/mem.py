from app.memory import memory_conversation, memory_retrival
from datetime import datetime
from typing import Dict


async def get_candidate_memories(candidate_id:str,limit:int=10):
    try:
        memories = await memory_retrival.get_memories(user_id=candidate_id,limit=limit)
        return memories.get("results",[])
    except Exception as e:
        print(f"Error at get_candidate_memories :-: {e}")


async def get_conversation_memories(candidate_id:str,limit:int=10):
    try:
        memories = await memory_conversation.get_memories(user_id=candidate_id,limit=limit)
        return memories.get("results",[])
    except Exception as e:
        print(f"Error at get_conversation_memories :-: {e}")


async def get_search_candidate_memories(candidate_id:str,query:str,limit:int=10):
    try:
        memories = await memory_retrival.search(query=query,user_id=candidate_id,limit=limit)
        return memories.get("results",[])
    except Exception as e:
        print(f"Error at get_search_candidate_memories :-: {e}")
        
        
async def get_search_conversation_memories(candidate_id:str,query:str,limit:int=10):
    try:
        memories = await memory_conversation.search(query=query,user_id=candidate_id,limit=limit)
        return memories.get("results",[])
    except Exception as e:
        print(f"Error at get_search_conversation_memories :-: {e}")
        

async def add_candidate_memories(candidate_id:str,session_id:str,message:str):
    try:
        metadata = {"type":"conversation","session_id":session_id,"timestamp":datetime.now()}
        await memory_retrival.add(message,user_id=candidate_id,metadata=metadata)
    except Exception as e:
        print(f"Error at add_candidate_memories :-: {e}")
        
        
async def add_conversation_memories(candidate_id:str,interview_data:Dict[str,any],session_id:str):
    try:
        metadata = {"type":"conversation","session_id":session_id,"timestamp":datetime.now()}
        memory_text = f"Question : {interview_data.get('question','')}"
        memory_text += f"Answer : {interview_data.get('answer','')}"
        memory_text += f"Evaluation : {interview_data.get('evaluation','')}"
        await memory_conversation.add(message=memory_text,user_id=candidate_id,metadata=metadata)
    except Exception as e:
        print(f"Error at add_conversation_memories :-: {e}")