from mem0 import AsyncMemory
from dotenv import find_dotenv, load_dotenv
import os

# Load environment variables from .env file
load_dotenv(find_dotenv())

# --- Consolidated Base Configuration ---
# Both memory instances share the same core services (Neo4j, OpenAI),
# so we define this configuration once.
base_mem0_config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": os.getenv("NEO4J_URI"),
            "username": os.getenv("NEO4J_USERNAME"),
            "password": os.getenv("NEO4J_PASSWORD")
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": os.getenv("EMBEDDING_MODEL"),
            "api_key": os.getenv("EMBEDDING_API_KEY")
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": os.getenv("MODEL_LLM_1"),
            "api_key": os.getenv("MODEL_LLM_1_API_KEY")
        }
    }
}

# --- Specific Configuration for Each Memory Type ---

# 1. Configuration for the conversation memory
# It's good practice to use a separate collection for conversation history.
mem0_conversation_config = {
    **base_mem0_config,
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": os.getenv("QDRANT_URL"),
            "collection_name": os.getenv("QDRANT_COLLECTION_NAME", "interview_conversations"),
            "embedding_model_dims": 1536
        }
    }
}

# 2. Configuration for the resume/retrieval memory
# This memory will use a different collection to store resume data.
mem0_retrieval_config = {
    **base_mem0_config,
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": os.getenv("QDRANT_URL"),
            "collection_name": os.getenv("QDRANT_RESUME_COLLECTION", "resume_retrieval"),
            "embedding_model_dims": 1536
        }
    }
}


# --- Asynchronous Initializer ---

# We declare the variables here and will initialize them inside the async function.
memory_conversation: AsyncMemory | None = None
memory_retrival: AsyncMemory | None = None

async def initialize_memories():
    """
    Asynchronously initializes the memory instances.
    This function should be called once within your application's async context.
    """
    global memory_conversation, memory_retrival
    
    # Initialize only if they haven't been already to avoid re-creating them.
    if memory_conversation is None:
        print("Initializing conversation memory...")
        memory_conversation = await AsyncMemory.from_config(mem0_conversation_config)
    
    if memory_retrival is None:
        print("Initializing retrieval memory...")
        memory_retrival = await AsyncMemory.from_config(mem0_retrieval_config)
        
    return memory_conversation, memory_retrival