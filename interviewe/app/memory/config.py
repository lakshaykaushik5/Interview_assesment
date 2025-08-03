from mem0 import Memory,AsyncMemory
from dotenv import find_dotenv,load_dotenv
import asyncio
import os

load_dotenv(find_dotenv())


mem0_config = {
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "url":os.getenv("QDRANT_URL"),
            "collection_name":os.getenv("QDRANT_COLLECTION_NAME"),
            "embedding_model_dims":1536
        }
    },
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url":os.getenv("NEO4J_URI"),
            "username":os.getenv("NEO4J_USER"),
            "password":os.getenv("NEO4J_PASSWORD")
        }
    },
    "embedder":{
        "provider":"openai",
        "config":{
            "model":os.getenv("EMBEDDING_MODEL"),
            "api_key":os.getenv("EMBEDDING_API_KEY")
        }
    },
    "llm":{
        "provider":"openai",
        "config":{
            "model":os.getenv("MODEL_1_NAME"),
            "api_key":os.getenv("MODEL_1_API_KEY")
        }
    }
}


mem0_conversation_config = {
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "url":os.getenv("QDRANT_URL"),
            "collection_name":os.getenv("QDRANT_COLLECTION_NAME"),
            "embedding_model_dims":1536
        }
    },
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url":os.getenv("NEO4J_URI"),
            "username":os.getenv("NEO4J_USER"),
            "password":os.getenv("NEO4J_PASSWORD")
        }
    },
    "embedder":{
        "provider":"openai",
        "config":{
            "model":os.getenv("EMBEDDING_MODEL"),
            "api_key":os.getenv("EMBEDDING_API_KEY")
        }
    },
    "llm":{
        "provider":"openai",
        "config":{
            "model":os.getenv("MODEL_1_NAME"),
            "api_key":os.getenv("MODEL_1_API_KEY")
        }
    }
}


memory_conversation = AsyncMemory.from_config(mem0_conversation_config)
memory_retrival = AsyncMemory.from_config(mem0_config)
