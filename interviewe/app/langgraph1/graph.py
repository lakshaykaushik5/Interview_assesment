from langgraph.graph import StateGraph, START,END
from .states import InterviewState
from .nodes import question_generator_node,sentiment_analysis_node,supervisor_node,response_evaluator_node



def route_supervise(state:InterviewState):
    """
    Routes to appropriate subgraph based on the supervisor's decission.
    """
    return state.get("next_action","screening")


def route_evaluation(state:InterviewState):
    
    """
    Decides the next step after evaluating the candidate's response .
    - If a follow-up is needed, ask another question in the same context.
    - If the stage is done, go back to supervisor to change topics.
    - If the interview should conclude, end the graph
    """
    
    if state.get("follow_up_needed",False):
        return "follow_up"

    if len(state.get("question_history",[])) > 5:
        if state.get("current_stage") == "conclusion":
            return "end"
        else:
            return "next_stage"
    else:
        return "continue_stage"

graph = StateGraph(InterviewState)

graph.add_node("supervisor",supervisor_node)
graph.add_node("question_generator",question_generator_node)
graph.add_node("response_evaluator",response_evaluator_node)
graph.add_node("sentiment_analyzer",sentiment_analysis_node)



graph.add_edge(START,"supervisor")
graph.add_conditional_edges("supervisor",route_supervise,{
    "screening_subgraph":"question_generator",
    "evaluation_subgraph":"question_generator",
    "conclusion_node":END
})


graph.add_edge("question_generator","sentiment_analyzer")
graph.add_edge("sentiment_analyzer","response_evaluator")


graph.add_conditional_edges(
    "response_evaluator",
    route_evaluation,
    {
        "follow_up":"question_generator",
        "continue_stage":"question_generator",
        "next_stage":"supervisor",
        "end":END
    }
)


app = graph.compile()