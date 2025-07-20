from mem0 import Memory
from dotenv import load_dotenv,find_dotenv
import os

load_dotenv(find_dotenv())


required_keys = [
    "EMBEDDING_API_KEY", "EMBEDDING_MODEL", "QDRANT_URL",
    "QDRANT_COLLECTION_NAME", "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"
]

for key in required_keys:
    if os.getenv(key) is None:
        print(f"[ERROR] Missing env var: {key} +++++++++++++++++++++++++++++++++\n\n")
        


mem0_config = {
    "vector_store": {
        "provider":"qdrant",
        "config": {
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
    "llm": {
        "provider": "openai",
        "config": {
            "model": os.getenv("MODEL_1_NAME"),
            "api_key": os.getenv("MODEL_1_API_KEY")
        }
    }

}


memory = Memory.from_config(mem0_config)