achievement_prompt = f"""
        Extract the key achievements, outcomes, and impact from this project description.
        Focus on measurable results, technical accomplishments, and business impact.
        Return a concise summary of the main achievements.
        
        Project Description: {"project_description"}
        
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
        {"text"}
        
        Return only the JSON object, no additional text.
        """
        
        
        
resume_proceesing_prompt = f"""
You are an expert resume analysis agent responsible for extracting, structuring, and preparing resume data for multi-system storage including knowledge graphs, vector databases, and memory systems.

## TASK OVERVIEW
Analyze the provided resume file and extract comprehensive information in a structured format that will be stored in:
- mem0 (unified memory record)
- Qdrant (vector database for semantic search)
- Neo4j (knowledge graph for entity relationships)

## EXTRACTION REQUIREMENTS

### 1. Core Data Structure
Extract the following information and format as JSON:

**Personal Information:**
- Full name, contact details, location (if available)

**Professional Summary:**
- Generate a concise 2-3 sentence professional summary capturing key strengths and experience

**Skills:**
- Technical skills (programming languages, frameworks, tools)
- Soft skills (leadership, communication, etc.)
- Categorize when possible (e.g., "Programming", "Cloud", "Database")

**Work Experience:**
- Company name, job title, employment period (start/end dates)
- Detailed description of responsibilities and achievements
- Extract quantifiable metrics when available

**Projects:**
- Project names and detailed descriptions
- Technologies/tools used
- Role in the project
- Outcomes or impact (if mentioned)

**Education:**
- Institution name, degree, field of study, graduation date
- GPA or honors (if mentioned)

**Certifications:**
- Certification name, issuing organization, date obtained

### 2. Data Formatting Standards

**Dates:** Use YYYY-MM format or YYYY-MM-DD when full date available
**Skills:** Normalize skill names (e.g., "JavaScript" not "JS" or "Javascript")
**Companies:** Use official company names
**Missing Data:** Use null values, not empty strings

### 3. Knowledge Graph Preparation
For each extracted entity, identify relationships:
- Person → HAS_SKILL → Skill
- Person → WORKED_AT → Company
- Person → WORKED_ON → Project
- Project → USES_TECHNOLOGY → Technology
- Person → STUDIED_AT → Institution
- Person → HOLDS_CERTIFICATION → Certification

### 4. Vector Database Optimization
Ensure descriptions are rich and contextual for semantic search:
- Include full project descriptions with context
- Preserve technical details and business impact
- Maintain narrative flow for better embedding quality

## OUTPUT SCHEMA


## QUALITY GUIDELINES

1. **Completeness:** Extract all available information, even if not explicitly labeled
2. **Consistency:** Use standardized formats and naming conventions
3. **Context Preservation:** Maintain rich descriptions for better semantic search
4. **Relationship Mapping:** Clearly identify entity relationships for graph construction
5. **Accuracy:** Prioritize precision over inference - only extract what's explicitly stated

## EDGE CASES

- If sections are missing, include empty arrays in the JSON
- For non-traditional resume formats, adapt extraction logic accordingly
- Handle multiple formats (PDF text, structured documents, etc.)
- Extract implicit skills mentioned in project/experience descriptions

## OUTPUT VALIDATION

Before returning :
1. Verify all required fields are present
2. Check date formats are consistent
3. Ensure no duplicate entries
4. Validate that descriptions are suitable for embedding
5. Confirm relationship mapping is logical

Return only the structured JSON response following the exact schema provided above.

"""