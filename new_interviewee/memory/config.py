from mem0 import AsyncMemory, Memory
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())


base_mem0_config = {
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url":os.getenv("NEO4J_URI"),
            "username":os.getenv("NEO4J_USERNAME"),
            "password":os.getenv("NEO4J_PASSWORD"),
        }
    },
    "embedder":{
        "provider":"openai",
        "config":{
            "model":os.getenv("EMBEDDING_MODEL"),
            "api_key":os.getenv("EMBEDDING_API_KEY"),
            
        }
    },
    "llm":{
        "provider":"openai",
        "config":{
            "model":os.getenv("MODEL_LLM_1"),
            "api_key":os.getenv("MODEL_LLM_1_API_KEY")
        }
    }
}


mem0_conversation_config = {
    **base_mem0_config,
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "url":os.getenv("QDRANT_URL"),
            "collection_name":os.getenv("QDRANT_COLLECTION_NAME","interview_conversation"),
            "embedding_model_dims":1536
        }
    }
}


mem0_resume_retrieval_memory = {
    **base_mem0_config,
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "url":os.getenv("QDRANT_URL"),
            "collection_name":os.getenv("QDRANT_RESUME_COLLECTION","resume_retrieval"),
            "embedding_model_dims":1536
        }
    }
}


memory_conversation : AsyncMemory | None = None
memory_resume : AsyncMemory | None = None


async def initialize_memory():
    global memory_conversation,memory_resume
    
    if memory_resume is None:
        print("Intializing resume retrieval memory . . . . . . ")
        memory_resume = await AsyncMemory.from_config(mem0_resume_retrieval_memory)
        
    if memory_conversation is None:
        print("Intializing conversation memory . . . . . .  ")
        memory_conversation = await AsyncMemory.from_config(mem0_conversation_config)
        
    
    return memory_resume,memory_conversation

memory_resume_sync = Memory.from_config(mem0_resume_retrieval_memory)
memory_conversation_sync = Memory.from_config(mem0_conversation_config)