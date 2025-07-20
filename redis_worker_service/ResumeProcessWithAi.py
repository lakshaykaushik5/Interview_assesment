from prompts import resume_proceesing_prompt
from openai import AsyncOpenAI

from dotenv import load_dotenv,find_dotenv

import os


load_dotenv(find_dotenv())



async def resume_processing_with_ai(file_path:str):
    
    print("here ----------------------- 1-1----------------------")
    client = AsyncOpenAI(api_key=os.getenv("MODEL_1_API_KEY"))
    print("here ----------------------- 1-2----------------------")
    
    
    file = await client.files.create(
        file=open(file_path, "rb"),
        purpose="user_data"
    )


    response = await client.responses.create(
        model=os.getenv("MODEL_1_NAME"),
        input=[ 
            {
                "role":"user",
                "content":[
                    {
                        "type":"input_file",
                        "file_id":file.id
                    },
                    {
                        "type":"input_text",
                        "text": resume_proceesing_prompt
                    }
                ]
            }
        ]
    )
    print("here ----------------------- 1-3----------------------")

    final_data =response.output_text 
    print(final_data)
    return final_data


