import PyPDF2
import io
from typing import List
import openai
from app.core.config import settings

class PDFService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
    
    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")
    
    async def extract_questions_from_text(self, text: str) -> List[str]:
        """Use OpenAI to extract questions from PDF text - ONLY for question extraction"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        prompt = f"""
        Extract all questions from the following RFP document text. 
        Return ONLY the questions, one per line, without numbering or bullet points.
        Do not provide answers or explanations.
        
        Text: {text[:4000]}
        
        Questions:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            questions_text = response.choices[0].message.content
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            return questions
        except Exception as e:
            raise ValueError(f"Error extracting questions: {str(e)}")
    
    def extract_questions_simple(self, text: str) -> List[str]:
        """Simple question extraction without OpenAI (fallback)"""
        import re
        
        # Look for question patterns
        question_patterns = [
            r'[?]',  # Questions ending with ?
            r'please provide',
            r'please share',
            r'kindly provide',
            r'what is',
            r'what are',
            r'how does',
            r'how do',
            r'can you',
            r'could you'
        ]
        
        sentences = re.split(r'[.!?]\s+', text)
        questions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Minimum length
                for pattern in question_patterns:
                    if re.search(pattern, sentence.lower()):
                        questions.append(sentence)
                        break
        
        return questions[:20]  # Limit to 20 questions
