achievement_prompt = f"""
        Extract the key achievements, outcomes, and impact from this project description.
        Focus on measurable results, technical accomplishments, and business impact.
        Return a concise summary of the main achievements.
        
        Project Description: {project_description}
        
        Return only the achievements summary, no additional text.
        """


extraction_prompt = f"""
        Extract structured information from this resume text. Return a JSON object with the following structure:
        {{
            "personal_info": {{
                "name": "string",
                "email": "string", 
                "phone": "string",
                "location": "string",
                "linkedin": "string",
                "github": "string"
            }},
            "professional_summary": "string",
            "skills": {{
                "technical_skills": ["skill1", "skill2"],
                "soft_skills": ["skill1", "skill2"],
                "tools_frameworks": ["tool1", "tool2"],
                "programming_languages": ["lang1", "lang2"]
            }},
            "experience": [
                {{
                    "company": "string",
                    "position": "string", 
                    "start_date": "string",
                    "end_date": "string",
                    "duration": "string",
                    "responsibilities": ["resp1", "resp2"],
                    "achievements": ["achievement1", "achievement2"]
                }}
            ],
            "education": [
                {{
                    "institution": "string",
                    "degree": "string",
                    "field_of_study": "string",
                    "graduation_year": "string",
                    "gpa": "string"
                }}
            ],
            "projects": [
                {{
                    "name": "string",
                    "description": "string",
                    "technologies": ["tech1", "tech2"],
                    "url": "string"
                }}
            ],
            "certifications": [
                {{
                    "name": "string",
                    "issuer": "string",
                    "date": "string",
                    "credential_id": "string"
                }}
            ],
            "years_of_experience": "number",
            "seniority_level": "string"
        }}
        
        Resume Text:
        {text}
        
        Return only the JSON object, no additional text.
        """
        