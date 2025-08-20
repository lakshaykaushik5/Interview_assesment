import asyncio
from langgraph1.graph import app
from langgraph1.states import InterviewState
from langchain_core.messages import HumanMessage


async def run_interview_test():
    
    initial_state = InterviewState(
        messages=[HumanMessage(content="Hi I am ready for the Interview.")],
        candidate_id="4b008704-8ce1-4b91-8c5c-7aa2d4dda49b",
        session_id="",
        current_stage="screening",
        interview_context={
            "role":"Software Engineer",
            "resume_summary":"A full stack developer with 2 years of experience"
        },
        question_history = [],
        evaluation_scores={},
        next_action=None
    )
    
    print("--- Starting Interview Test ---")
    print(f"Initial State: current stage = '{initial_state['current_stage']}'")
    print('-'*12)
    print('\n')
    
    
    async for event in app.astream_events(initial_state,version="v1"):
        event_type = event["event"]
        
        if event_type in ("on_chain_start","on_chain_end"):
            node_name = event["name"]
            
            if event_type == "on_chain_start":
                print(f"--- Running Node : '{node_name}' ---")
            else:
                output = event["data"].get("output")
                print(f"--- Finished Node : '{node_name}' ---")
                print("Output :")
                
                if isinstance(output,dict):
                    if "next_action" in output:
                        print(f"  - next_section : {output['next_action']}")
                    
                    if 'messages' in output and output['messages']:
                        print(f"  - last_mesage : {output['messages'][-1].content}")
                        
                
                print("-"*12)
                print("\n")
                
                
                
def main():
    try:
        asyncio.run(run_interview_test())
    except KeyboardInterrupt:
        print("\n --- stopped ---")