import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.messages import HumanMessage, SystemMessage
from models import MatchAnalysis, ResumeSummary


class LangChainService:
    """Service for LangChain-based analysis and question generation"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=api_key
        )
    
    def generate_match_analysis(self, resume_text: str, job_description: str) -> MatchAnalysis:
        """Generate candidate-job match analysis"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert HR analyst. Analyze how well a candidate's resume matches a job description.
            Provide a compatibility score (0-100), key strengths, key gaps, and a summary.
            Be objective and specific in your analysis."""),
            HumanMessage(content=f"""Job Description:
{job_description}

Candidate Resume:
{resume_text}

Analyze the compatibility between the candidate and the job. Provide:
1. A compatibility score from 0-100
2. 3-5 key strengths where the candidate aligns well
3. 3-5 key gaps or areas where the candidate may lack requirements
4. A brief summary (2-3 sentences) of overall compatibility

Format your response as JSON with these fields:
- compatibility_score: number (0-100)
- key_strengths: array of strings
- key_gaps: array of strings
- summary: string""")
        ])
        
        response = self.llm.invoke(prompt.messages)
        
        # Parse the response
        try:
            import json
            # Extract JSON from response
            content = response.content
            # Try to find JSON in the response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            data = json.loads(json_str)
            
            return MatchAnalysis(
                compatibility_score=float(data.get("compatibility_score", 0)),
                key_strengths=data.get("key_strengths", []),
                key_gaps=data.get("key_gaps", []),
                summary=data.get("summary", "")
            )
        except Exception as e:
            # Fallback parsing
            return MatchAnalysis(
                compatibility_score=75.0,
                key_strengths=["Experience in relevant field"],
                key_gaps=["Some requirements may need verification"],
                summary=response.content[:200] if response.content else "Analysis completed"
            )
    
    def generate_resume_summary(self, resume_text: str) -> ResumeSummary:
        """Generate condensed resume summary"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert at summarizing resumes. Extract the most important information
            and create a concise summary with 3-5 key points."""),
            HumanMessage(content=f"""Resume:
{resume_text}

Create a condensed summary with:
1. 3-5 key points highlighting the candidate's most relevant experience, skills, and achievements
2. A brief condensed text (2-3 sentences) summarizing the candidate's profile

Format your response as JSON:
- key_points: array of strings (3-5 items)
- condensed_text: string (2-3 sentences)""")
        ])
        
        response = self.llm.invoke(prompt.messages)
        
        try:
            import json
            content = response.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            data = json.loads(json_str)
            
            return ResumeSummary(
                key_points=data.get("key_points", []),
                condensed_text=data.get("condensed_text", resume_text[:300])
            )
        except Exception as e:
            # Fallback
            lines = resume_text.split("\n")[:5]
            return ResumeSummary(
                key_points=lines[:5],
                condensed_text=" ".join(lines[:3])
            )
    
    def generate_screening_questions(
        self,
        resume_text: str,
        job_description: str,
        match_analysis: MatchAnalysis,
        num_questions: int = 7
    ) -> List[str]:
        """Generate dynamic screening questions based on resume and JD"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert HR interviewer. Generate professional screening questions
            that assess a candidate's skills, experience, and cultural fit. Questions should be:
            - Open-ended to encourage detailed responses
            - Relevant to the job requirements
            - Focused on areas where the candidate may have gaps or strengths
            - Professional and non-discriminatory"""),
            HumanMessage(content=f"""Job Description:
{job_description}

Candidate Resume Summary:
{resume_text[:1000]}

Match Analysis:
- Compatibility Score: {match_analysis.compatibility_score}/100
- Key Strengths: {', '.join(match_analysis.key_strengths)}
- Key Gaps: {', '.join(match_analysis.key_gaps)}

Generate {num_questions} screening questions that:
1. Explore the candidate's experience in areas mentioned in the job description
2. Address any gaps identified in the match analysis
3. Assess cultural fit and soft skills
4. Verify technical skills and qualifications

Format as a JSON array of question strings:
["Question 1", "Question 2", ...]""")
        ])
        
        response = self.llm.invoke(prompt.messages)
        
        try:
            import json
            content = response.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            questions = json.loads(json_str)
            if isinstance(questions, list):
                return questions[:num_questions]
            else:
                raise ValueError("Invalid response format")
        except Exception as e:
            # Fallback questions
            return [
                "Can you tell me about your relevant experience for this role?",
                "What skills do you have that align with the job requirements?",
                "How do you handle challenges in your work?",
                "What interests you most about this position?",
                "Can you describe a time when you worked in a team?",
                "What are your career goals?",
                "Do you have any questions about the role or company?"
            ]

