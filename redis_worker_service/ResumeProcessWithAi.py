from prompts import resume_proceesing_prompt
from openai import AsyncOpenAI

from dotenv import load_dotenv,find_dotenv
import json

import os


load_dotenv(find_dotenv())



async def resume_processing_with_ai(file_path:str):
    client = AsyncOpenAI()

    response = await client.responses.create(
        model=os.getenv("MODEL_2_NAME"),
        input=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"input_file",
                        "file_url":file_path
                    },
                    {
                        "type":"input_text",
                        "text": resume_proceesing_prompt
                    }
                ]
            }
        ]
    )
    final_data =response.output_text 
    print(final_data)
    return final_data


