from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class InterviewState(TypedDict):
    messages:Annotated[List[BaseMessage],add_messages]
    candidate_id:str
    session_id:str
    current_stage:str
    interview_context:Dict[str,Any]
    question_history:List[Dict[str,Any]]
    evaluation_scores:Dict[str,Any]
    follow_up_needed:bool
    memories:List[Dict[str,Any]]
    next_action:Optional[str]
    

class InterviewEvent(TypedDict):
    event_type:str
    data:Dict[str,Any]
    timestamp:str
    session_id:str