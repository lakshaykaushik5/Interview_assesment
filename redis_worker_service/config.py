from mem0 import Memory
from dotenv import load_dotenv,find_dotenv
import os

load_dotenv(find_dotenv())



mem0_config = {
    "vector_store": {
        "provider":"qdrant",
        "config": {
            "url":os.getenv("QDRANT_URL"),
            "collection_name":os.getenv("COLLECTION_NAME"),
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
    }
}


memory = Memory.from_config(mem0_config)