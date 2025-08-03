

def question_generator_prompt(candidate_context,memory_resume,memory_conv,state):
    return f"""
    Your are an expert interviewer. Generate relevant interview question based on 

        Candidate Context : {candidate_context}
        Resume Content : {memory_resume}
        Previous Interaction: {memory_conv}
        Current Stage : {state.get("current_stage","screening")}
        
        Generate a thoughtful question that explores the candidate's experience and skills

    """
    
def response_evaluator_prompt(last_message_content):
    return f"""
        Evaluate this Interveiw response on multiple dimensions:
        
        Response :{last_message_content}
        - Technical competency
        - Communication clarity
        - Problem Solving approach
        - Cultural fit indicators
        
        Also determine if a follow-up question is needed.
        Return JSON format with stores and follow_up_needed boolean. 
    """