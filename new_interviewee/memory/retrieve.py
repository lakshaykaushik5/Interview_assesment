import os 
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from typing import List
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


QUADRANT_URL = os.getenv("QDRANT_URL")
EMBEDDING_DIM = 1536


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


QUERY_VECTOR = [0.01] * EMBEDDING_DIM

TOP_K = 5



def search_qdrant(client:QdrantClient,qdrant_collection:str,query_vector:List[float],top_k :int=5):
    result = client.search(
        collection_name=qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    
    return result


def search_neo4j(driver:GraphDatabase.driver,node_ids:List[int]):
    cypher = """ 
        MATCH(n)
        WHERE id(n) IN $ids
        OPTIONAL MATCH (n)-[R]-(m)
        RETURN n,r,m
    """
    
    with driver.session() as session:
        result = session.run(cypher,id=node_ids)
        return list(result)
    
    

def memory_retrieval(type:str="resume"):
    
    QUADRANT_COLLECTION=None
    
    if type == "resume":
        QUADRANT_COLLECTION = os.getenv("QDRANT_RESUME_COLLECTION")
    else:
        QUADRANT_COLLECTION = os.getenv("QDRANT_CONVERSATION_COLLECTION")


    qdrant = QdrantClient(url=QUADRANT_URL)
    
    print(f"Searching Qdrant Collection {QUADRANT_COLLECTION} . . . .")
    
    qdrant_result = search_qdrant(qdrant,QUADRANT_COLLECTION,QUERY_VECTOR,TOP_K)
    
    print(f"\n Qdrant Search Results :")
    
    neo4j_ids = []
    
    for hit in qdrant_result:
        print(f" * ID :{hit.id} ,Source :{hit.score}, payload :{hit.payload}")
        
        if "neo4j_id" in hit.payload:
            neo4j_ids.append(hit.payload["neo4j_id"])
            
    
    if not neo4j_ids:
        print("\n No ids found in payload")
        return 

    neo4j_driver = GraphDatabase.driver(NEO4J_URI,auth=(NEO4J_USER,NEO4J_PASSWORD))
    
    graph_records = search_neo4j(neo4j_driver,neo4j_ids)
    
    neo4j_driver.close()    
    return graph_records,qdrant_result
