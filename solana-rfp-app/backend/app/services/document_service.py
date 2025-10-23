import PyPDF2
import docx
import pandas as pd
import io
from typing import List, Optional
import openai
from app.core.config import settings

class DocumentService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
    
    async def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text from various document formats"""
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return await self.extract_text_from_pdf(file_content)
        elif file_extension in ['docx', 'doc']:
            return await self.extract_text_from_docx(file_content)
        elif file_extension in ['xlsx', 'xls']:
            return await self.extract_text_from_excel(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
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
    
    async def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from Word document"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error extracting DOCX text: {str(e)}")
    
    async def extract_text_from_excel(self, file_content: bytes) -> str:
        """Extract text from Excel file"""
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(io.BytesIO(file_content))
            text = ""
            
            # Process each sheet
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                text += f"Sheet: {sheet_name}\n"
                
                # Convert DataFrame to text
                for index, row in df.iterrows():
                    row_text = " | ".join([str(cell) for cell in row.values if pd.notna(cell)])
                    if row_text.strip():
                        text += row_text + "\n"
                text += "\n"
            
            return text
        except Exception as e:
            raise ValueError(f"Error extracting Excel text: {str(e)}")
    
    async def extract_questions_from_text(self, text: str) -> List[str]:
        """Use OpenAI to extract questions from document text"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        prompt = f"""
        Extract all questions from the following document text. 
        Return ONLY the questions, one per line, without numbering or bullet points.
        Do not provide answers or explanations.
        Focus on questions that would be relevant for an RFP (Request for Proposal) context.
        
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
        
        # Your existing question extraction logic
        QUESTION_TRIGGERS = [
            "please provide", "please share", "kindly provide", "kindly share",
            "provide a", "provide the", "provide your",
            "please tell us", "let us know", "could you", "can you",
            "we would appreciate", "we'd appreciate", "we would like to request",
            "we'd like to request", "we request", "request if you can share",
            "we'd like to ask", "we would like to ask",
            "how does", "how do", "how is", "how are", "how will",
            "what is", "what are", "what's", "which", "when", "why",
            "justify", "outline", "explain", "describe", "bsp:"
        ]
        
        BULLET_RE = re.compile(r"^\s*(?:[\-\*\u2022]|\d+\)|\d+\.)\s+")
        
        def looks_like_question(s: str) -> bool:
            low = s.lower().strip()
            if low.endswith("?"):
                return True
            if BULLET_RE.match(s) and any(tr in low for tr in QUESTION_TRIGGERS):
                return True
            if any(tr in low for tr in QUESTION_TRIGGERS):
                return True
            if re.match(r"^\s*(provide|outline|explain|describe|justify)\b", low):
                return True
            if re.match(r"^\s*(bsp|regulator)\s*:\s*", low):
                return True
            return False
        
        def split_on_question_marks(s: str):
            # Don't split compound questions - treat the whole text as one question if it contains question marks
            s = s.strip()
            if not s:
                return []
            
            # If it's a single line with multiple question marks, treat as one compound question
            if '\n' not in s and s.count('?') > 1:
                return [s]
            
            # Otherwise, split on question marks as before
            parts = re.split(r"(\?)", s)
            out, acc = [], ""
            for seg in parts:
                acc += seg
                if seg == "?":
                    out.append(acc.strip()); acc = ""
            if acc.strip():
                out.append(acc.strip())
            return out
        
        # Clean and extract questions
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        candidates = []
        
        for line in lines:
            for piece in split_on_question_marks(line):
                if looks_like_question(piece):
                    candidates.append(piece)
        
        # Remove duplicates and short questions
        seen, questions = set(), []
        for q in candidates:
            qn = q.lower().strip()
            if len(qn) >= 15 and qn not in seen:
                seen.add(qn)
                questions.append(q.strip())
        
        return questions
