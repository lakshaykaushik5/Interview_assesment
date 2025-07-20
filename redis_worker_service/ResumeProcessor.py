# import asyncio
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain.document_loaders import PyPDFLoader
# from langchain_openai import ChatOpenAI
# from langchain.schema import HumanMessage

# import os
# from dotenv import load_dotenv,find_dotenv
# import json
# from datetime import datetime

# from config import memory
# from prompts import achievement_prompt,extraction_prompt

# load_dotenv(find_dotenv())



# class ResumeProcessor:
#     def __init__(self):
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function = len,
#         )
        
#         self.embeddings = OpenAIEmbeddings(
#             openai_api_key=os.getenv("EMBEDDING_API_KEY"),
#             model = os.getenv("EMBEDDING_MODEL")
#         )
        
#     async def extract_text_from_pdf(self,file_path:str):
#         try:
#             loader = PyPDFLoader(file_path=file_path)
#             pages = loader.load()
#             text = "\n".join([page.page_content for page in pages])
#             return text
#         except Exception as e:
#             print(f"Error extracting text from file path {file_path} :: {str(e)}")
            
#     async def extract_resume_entities(self,text:str):
        
#         llm = ChatOpenAI(
#             model=os.getenv("MODEL_1_NAME"),
#             openai_api_key = os.getenv("MODEL_1_API_KEY"),
#         )
                
#         try:
#             response = await llm.invoke([HumanMessage(content=extraction_prompt)])
#             entities = json.loads(response.content)
#             return entities
#         except Exception as e:
#             print(f"Error at extract_text_from_pdf :: {str(e)}")
#             return self.basic_entity_extraction
        
    
#     async def extract_project_achievements(self,project_description:str):
#         llm = ChatOpenAI(
#             model=os.getenv("MODEL_1_NAME"),
#             openai_api_key = os.getenv("MODEL_1_API_KEY")
#         )
        
        
#         try:
#             response = await llm.invoke([HumanMessage(content=achievement_prompt)])
#             return response.content.strip()
#         except Exception as e:
#             print(f"Error at extract_project_achievements :: {str(e)}")
#             return ""
        
        
#     async def basic_entity_extraction(self,text:str):
#         return {
#             "personal_info": {"name": "", "email": "", "phone": ""},
#             "professional_summary": "",
#             "skills": {"technical_skills": [], "soft_skills": []},
#             "experience": [],
#             "education": [],
#             "projects": [],
#             "certifications": [],
#             "years_of_experience": 0,
#             "seniority_level": "entry"
#         }
        
    
#     async def process_resume_with_mem0(self,file_path:str,id:str):
#         try:
#             text_content = await self.extract_text_from_pdf(file_path)
            
#             entities = await self.extract_resume_entities(text_content)
            
#             user_id = f"candidate_{id}"
            
#             chunks = self.text_splitter.split_text(text_content)
            
#             base_metadata = {
#                 "resume_id":id,
#                 "candidate_name":entities.get("personal_info",{}).get("name",""),
#                 "candidate_email":entities.get("personal_info",{}.get("email","")),
#                 "processed_time":datetime.now().isoformat(),
#                 "chunks_count":len(chunks),
#                 "years_of_experience":entities.get("years_of_experience",0),
#                 "seniority_level":entities.get("seniority_level","entry")
#             }
            
#             memories = []
            
#             for i,chunk in enumerate(chunks):
#                 memory_result = memory.add(
#                     messages=[{
#                         "role":"user",
#                         "content":f"resume sectioin : {chunk}"
#                     }],
#                     user_id=user_id,
#                     metadata={
#                         **base_metadata,
#                         "content_type":'resume_chunk',
#                         "chunk_index":i
#                     }
#                 )
                
#                 memories.append(memory_result)
            
#             if entities.get("professional_summary"):
#                 memory.add(
#                     messages=[{
#                         "role":"user",
#                         "content":f"Professional summary :{entities["professional_summary"]}"
#                     }],
#                     user_id=user_id,
#                     metadata={**base_metadata,"content_type":"professional_summary"}
#                 )
                
            

#             all_skills = []
#             if entities.get("skills"):
#                 skills_data = entities["skills"]
#                 for skill_category, skills_list in skills_data.items():
#                     if skills_list:
#                         all_skills.extend(skills_list)
                
#                 if all_skills:
#                     memory.add(
#                         messages=[{
#                             "role": "user",
#                             "content": f"Technical skills and expertise: {', '.join(all_skills)}"
#                         }],
#                         user_id=user_id,
#                         metadata={
#                             **base_metadata, 
#                             "content_type": "skills",
#                             "skills": all_skills,
#                             "skill_categories": skills_data
#                         }
#                     )
            
#             if entities.get("experience"):
#                 for exp in entities["experience"]:
#                     if exp.get("company") and exp.get("position"):
#                         exp_content = f"Worked as {exp['position']} at {exp['company']}"
#                         if exp.get("responsibilities"):
#                             exp_content += f". Responsibilities: {'. '.join(exp['responsibilities'])}"
#                         if exp.get("achievements"):
#                             exp_content += f". Achievements: {'. '.join(exp['achievements'])}"
                        
#                         memory.add(
#                             messages=[{
#                                 "role": "user",
#                                 "content": exp_content
#                             }],
#                             user_id=user_id,
#                             metadata={
#                                 **base_metadata,
#                                 "content_type": "experience",
#                                 "company": exp.get("company"),
#                                 "position": exp.get("position"),
#                                 "duration": exp.get("duration"),
#                                 "start_date": exp.get("start_date"),
#                                 "end_date": exp.get("end_date")
#                             }
#                         )
            
#             if entities.get("education"):
#                 for edu in entities["education"]:
#                     if edu.get("institution") and edu.get("degree"):
#                         edu_content = f"Studied {edu['degree']}"
#                         if edu.get("field_of_study"):
#                             edu_content += f" in {edu['field_of_study']}"
#                         edu_content += f" at {edu['institution']}"
#                         if edu.get("graduation_year"):
#                             edu_content += f" (graduated {edu['graduation_year']})"
                        
#                         memory.add(
#                             messages=[{
#                                 "role": "user",
#                                 "content": edu_content
#                             }],
#                             user_id=user_id,
#                             metadata={
#                                 **base_metadata,
#                                 "content_type": "education",
#                                 "institution": edu.get("institution"),
#                                 "degree": edu.get("degree"),
#                                 "field_of_study": edu.get("field_of_study"),
#                                 "graduation_year": edu.get("graduation_year")
#                             }
#                         )
            
#             if entities.get("projects"):
#                 for project in entities["projects"]:
#                     if project.get("name") and project.get("description"):
#                         project_content = f"Project: {project['name']}. Description: {project['description']}"
                        
#                         if project.get("technologies"):
#                             project_content += f" Technologies used: {', '.join(project['technologies'])}"
                            
#                             for tech in project["technologies"]:
#                                 memory.add(
#                                     messages=[{
#                                         "role": "user",
#                                         "content": f"Has experience with {tech} technology through project {project['name']}"
#                                     }],
#                                     user_id=user_id,
#                                     metadata={
#                                         **base_metadata,
#                                         "content_type": "technology_experience",
#                                         "technology": tech,
#                                         "project_name": project.get("name"),
#                                         "context": "project"
#                                     }
#                                 )
                        
#                         memory.add(
#                             messages=[{
#                                 "role": "user",
#                                 "content": project_content
#                             }],
#                             user_id=user_id,
#                             metadata={
#                                 **base_metadata,
#                                 "content_type": "project",
#                                 "project_name": project.get("name"),
#                                 "technologies": project.get("technologies", []),
#                                 "has_detailed_description": bool(project.get("description"))
#                             }
#                         )
                        
#                         if project.get("description"):
#                             achievements = await self._extract_project_achievements(project["description"])
#                             if achievements:
#                                 memory.add(
#                                     messages=[{
#                                         "role": "user",
#                                         "content": f"Project achievements from {project['name']}: {achievements}"
#                                     }],
#                                     user_id=user_id,
#                                     metadata={
#                                         **base_metadata,
#                                         "content_type": "project_achievements",
#                                         "project_name": project.get("name"),
#                                         "achievements": achievements
#                                     }
#                                 )
            
#             mem0_user_id = user_id
#             return mem0_user_id
            
            
                
#         except Exception as e:
#             print(f"Error in process_resume_with_mem0 :: {str(e)}")


# # class ResumeProcessorWithAi:
    