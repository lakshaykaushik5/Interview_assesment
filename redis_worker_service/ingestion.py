from langchain.text_splitter import RecursiveCharacterTextSplitter

from ResumeProcessWithAi import resume_processing_with_ai
from config import memory

import asyncio




async def injestion(file_path:str,user_id:str):
    
    try:
        if not file_path or not user_id:
            print(f"Error at injestion missing user_id,file_path :: {file_path} | {user_id}")
            return 
            
        ai_processed_resume_text = resume_processing_with_ai(file_path)
        
        text_splitters = RecursiveCharacterTextSplitter(
            chunk_size = 200,
            chunk_overlap = 50,
            length_function = len,
        )
        
        chunks = text_splitters.split_text(ai_processed_resume_text)
        
        memories = []
        
        resume_name = file_path.split('/')[-1]
        
        for i,chunk in enumerate(chunks):
            memory_result = memory.add(
                messages=[{
                    "role":"user",
                    "content":f"resume section {chunk}",
                    "metadata": {
                        "resume_name": resume_name,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_path": file_path
                    }

                }],
                user_id=user_id
                
            )
            memories.append(memory_result)
            
        return {
           "user_id": user_id,
           "resume_name": resume_name,
           "total_chunks": len(chunks)
        }
    except Exception as e:
        print(f"Error at injestion :: {str(e)}")


async def main():
    pass



if __name__=="__main__":
    asyncio.run(main())
