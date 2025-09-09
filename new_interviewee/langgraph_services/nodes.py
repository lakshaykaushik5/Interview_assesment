import os
from dotenv import load_dotenv,find_dotenv

from .state import InterviewState
from prompts import interview_plan_node_system_prompt,main_question_generator_and_eval_node

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph,START,END

from memory import memory_retrieval, memory_resume_sync, memory_conversation_sync

load_dotenv(find_dotenv())


llm = init_chat_model(
    model=os.getenv("MODEL_LLM_1"),
    api_key=os.getenv("MODEL_LLM_1_API_KEY")
)


def interview_plan_node(state:InterviewState)->InterviewState:
    "This is the node which generates Interview plan"
    
    memory_prompt = "Create a User Resume Summary include all details so that agent can generate interview plan"
    resume_memories = memory_resume_sync.search(query=memory_prompt)
    
    system_msg = interview_plan_node_system_prompt(resume_memories)
    system_prompt = SystemMessage(content=system_msg)
    
    response = llm.invoke(system_prompt)
    
    print(response," ----------------------- ")
    
    state["interview_plan"] = response.content
    return state
    
def main_interview_node(state:InterviewState)->InterviewState:
    "This is the main node that handle question generation and evaluation"
    
    interview_plan = state["interview_plan"]
    current_stage = state["current_stage"]
    conversation_history = state["history"][-10]
    conversation_graph_memory,conversation_vector_memory = memory_retrieval(type="conversation")
    
    system_msg = main_question_generator_and_eval_node(interview_plan,current_stage,conversation_history,conversation_graph_memory,conversation_vector_memory)
    system_prompt = SystemMessage(content=system_msg)
    
    response = llm.invoke(system_prompt)
    
    print(response," ------------------------- ")
    
    data = response.content
    
    next_action = data.get("next_action",None)
    
    confidence_score = data.get("evaluation").get("confidence_score")
    communication_score = data.get('evaluation').get('communication_score')
    technical_score = data.get('evaluation').get('technical_score')
    eval_summanry = data.get('evaluation').get('eval_summanry')
    
    if next_action != None:
        state["next_action"] = data.get('next_action')
    
    state["history"] = state["history"].append({
        "confidence_score":confidence_score,
        "communication_score":communication_score,
        "technical_score":technical_score,
        "eval_summanry":eval_summanry
    })
    
    state["question"] = data.get('next_question')
        
    
    return state


def conditional_edge(state:InterviewState):
    "This will decide the next stage"
    if state["next_action"] == "END_INTERVIEW":
        return "end"
    
    else:
        state["current_stage"] = state["next_action"]
        
        return "continue"
    


graph = StateGraph(InterviewState)

graph.add_node("interview_plan_node",interview_plan_node)
graph.add_node("main_interview_node",main_interview_node)

graph.add_edge(START,'interview_plan_node')
graph.add_edge('interview_plan_node','main_interview_node')

graph.add_conditional_edges(
    'main_interview_node',
    conditional_edge,
    {
        "continue":main_interview_node,
        "end":END
    }
)



