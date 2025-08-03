from langgraph.graph import StateGraph, START,END
from .states import InterviewState
from .nodes import question_generator_node,sentiment_analysis_node,supervisor_node,response_evaluator_node



def route_supervise(state:InterviewState):
    next_action = state.get("next_action","screening_subgraph")
    return next_action


def route_evaluation(state:InterviewState):
    if state.get("follow_up_needed",False):
        return "follow_up"
    elif state.get("current_stage"):
        return



graph = StateGraph(InterviewState)

graph.add_node("supervisor",supervisor_node)
graph.add_node("question_generator",question_generator_node)
graph.add_node("response_evaluator",response_evaluator_node)
graph.add_node("sentiment_analyzer",sentiment_analysis_node)



graph.add_edge(START,"supervisor")
graph.add_conditional_edges("supervisor",)