from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv,find_dotenv
import os
import json
from langgraph1 import InterviewEvent,InterviewState
from memory.config import initialize_memories
from prompts import question_generator_prompt,response_evaluator_prompt,sentiment_analysis_prompt
from datetime import datetime

load_dotenv(find_dotenv())


llm = ChatOpenAI(
    model=os.getenv('MODEL_LLM_1'),
    api_key=os.getenv("MODEL_LLM_1_API_KEY")
)
    


# Top level supervisor for hierarchical orchestration
async def supervisor_node(state:InterviewState):
    
    current_stage = state.get("current_stage","screening")
    
    if current_stage == "screening":
        return {'next_action':'screening_subgraph'}
    elif current_stage == "deep_evaluation":
        return {'next_action':'evaluation_subgraph'}
    elif current_stage == "conclusion":
        return {'next_action':'conclusion_node'}
    else:
        return {"next_action":'screening_subgraph'}
    

    

# Generate contextual question based on candidate's profile
async def question_generator_node(state:InterviewState):
    candidate_context = state.get("interview_context",{})
    candidate_id = state.get('candidate_id','')

    memory_conversation, memory_retrival = await initialize_memories()

    query = state["messages"][-1].content

    memory_resume = await memory_retrival.search(query=query,user_id=candidate_id)
    memory_conv = await memory_conversation.search(query=query,user_id=candidate_id) 
    
    
    memory_resume_text = "\n".join([mem.get("content", "") for mem in memory_resume.get("results", [])]) or "No relevant resume information found."
    memory_conv_text = "\n".join([mem.get("content", "") for mem in memory_conv.get("results", [])]) or "No prior conversation"
    
    
    follow_up_text = "This should be a follow-up question based on prior answers." if state.get("follow_up_needed") else ""

    
    system_prompt = question_generator_prompt(candidate_context,memory_resume_text,memory_conv_text,state) + follow_up_text
    
    
    
    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Generate the Next Interview Question")
    ])
    
    return {
        "messages":[response],
        "question_history":state.get("question_history",[]) + [{
            "question":response.content,
            "stage":state.get("current_stage"),
            "timestamp":str(datetime.now())
        }]
    }
    
    
async def response_evaluator_node(state:InterviewState):
    last_message = state["messages"][-1] if state["messages"] else None
    if not last_message:
        return {"evaluation_scores":{},"follow_up_needed":False}
    
    
    system_prompt = response_evaluator_prompt(last_message)
    
    evaluator_response_str = await llm.ainvoke([
        SystemMessage(content=system_prompt)
    ])
    evaluator_response = json.loads(evaluator_response_str.content)
    
    return {
        "evaluation_scores":evaluator_response,
        "follow_up_needed":evaluator_response.get("follow-up",False)
    }
    

async def sentiment_analysis_node(state:InterviewState):
    last_message = state["messages"][-1] if state["messages"] else None
    if not last_message:
        return {"sentiment":"neutral","confidence":0}
    
    system_prompt = sentiment_analysis_prompt(last_message)
    
    sentiment_report_str = await llm.ainvoke([
        SystemMessage(content=system_prompt)
    ])
    print("sentiment_report_str.content:", sentiment_report_str.content," ____________________________")

    sentiment_report = json.loads(sentiment_report_str.content)
    
    return {
        "question_history": {
            "sentiment": sentiment_report.get("sentiment", "neutral"),
            "confidence": sentiment_report.get("confidence", 0)
        }
    }