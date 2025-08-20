from typing import Annotated,Optional
from typing_extensions import TypedDict
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class ConversationHistory(TypedDict):
    question:str
    answer:str
    confidence_score:float
    communication_score:float
    technical_score:float
    timestamp:str
    eval_summanry:str

class InterviewState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]
    candidate_id:str
    session_id:str
    question:str
    follow_up_needed:bool
    timestamp:str
    next_action:Optional[str]
    history:list[ConversationHistory]
    interview_plan:dict
    current_stage:str
    