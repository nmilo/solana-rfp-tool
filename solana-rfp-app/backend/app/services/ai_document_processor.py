"""
AI-powered document processor for extracting Q&A pairs with embeddings
"""

import openai
import json
import pandas as pd
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.logger import main_logger, log_error
from app.core.supabase_config import get_supabase_service_client

class AIDocumentProcessor:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.supabase = get_supabase_service_client()
        self.embedding_model = "text-embedding-3-large"
    
    async def extract_qa_from_text(self, content: str, filename: str) -> List[Dict]:
        """
        Use GPT-4 to intelligently extract Q&A pairs from any text
        """
        try:
            main_logger.info(f"Extracting Q&A pairs from {filename}")
            
            prompt = f"""
            Extract all question and answer pairs from the following document.
            Return ONLY a JSON array of objects with "question" and "answer" fields.
            Be intelligent about matching questions to their answers even if they're separated.
            Clean up formatting and remove any metadata/headers.
            
            Document content:
            {content[:15000]}  # Limit to avoid token limits
            
            Return format:
            [
                {{"question": "What is X?", "answer": "X is..."}},
                {{"question": "How does Y work?", "answer": "Y works by..."}}
            ]
            
            IMPORTANT: Return ONLY the JSON array, no other text.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a document analysis expert. Extract Q&A pairs accurately and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=4000
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            qa_pairs = json.loads(result_text)
            
            main_logger.info(f"Extracted {len(qa_pairs)} Q&A pairs from {filename}")
            return qa_pairs
            
        except Exception as e:
            log_error(main_logger, e, "extract_qa_from_text", {"filename": filename})
            return []
    
    async def extract_qa_from_excel(self, file_path: str, filename: str) -> List[Dict]:
        """
        HYBRID APPROACH: Smart parsing + AI validation for Excel files
        Works perfectly with MXNB format and similar structured documents
        """
        try:
            main_logger.info(f"Extracting Q&A pairs from Excel: {filename}")
            
            # Read Excel file (all sheets)
            excel_file = pd.ExcelFile(file_path)
            all_qa_pairs = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                main_logger.info(f"Processing sheet: {sheet_name} with {len(df)} rows")
                
                # STRATEGY 1: MXNB-style detection (columns 3 & 5)
                qa_pairs = self._extract_mxnb_style(df)
                
                if len(qa_pairs) > 5:
                    main_logger.info(f"✅ Found {len(qa_pairs)} Q&A pairs using MXNB style")
                    all_qa_pairs.extend(qa_pairs)
                    continue
                
                # STRATEGY 2: Column name detection
                qa_pairs = self._extract_by_column_names(df)
                
                if len(qa_pairs) > 5:
                    main_logger.info(f"✅ Found {len(qa_pairs)} Q&A pairs using column names")
                    all_qa_pairs.extend(qa_pairs)
                    continue
                
                # STRATEGY 3: Pattern-based detection (any columns)
                qa_pairs = self._extract_by_patterns(df)
                
                if len(qa_pairs) > 5:
                    main_logger.info(f"✅ Found {len(qa_pairs)} Q&A pairs using patterns")
                    all_qa_pairs.extend(qa_pairs)
                    continue
                
                # STRATEGY 4: AI fallback for unstructured data
                main_logger.info(f"⚠️ Structured extraction found < 5 pairs, using AI...")
                text_content = df.to_string()
                ai_pairs = await self.extract_qa_from_text(text_content, sheet_name)
                all_qa_pairs.extend(ai_pairs)
            
            # Clean and deduplicate
            all_qa_pairs = self._clean_qa_pairs(all_qa_pairs)
            
            main_logger.info(f"✅ Total extracted: {len(all_qa_pairs)} Q&A pairs from {filename}")
            return all_qa_pairs
            
        except Exception as e:
            log_error(main_logger, e, "extract_qa_from_excel", {"filename": filename})
            return []
    
    def _extract_mxnb_style(self, df: pd.DataFrame) -> List[Dict]:
        """
        Extract Q&A from MXNB format: Col 3 = Question, Col 5 = Answer
        """
        qa_pairs = []
        
        try:
            # MXNB format uses columns 3 and 5
            if len(df.columns) >= 6:
                for i, row in df.iterrows():
                    # Skip header rows
                    if i == 0:
                        continue
                    
                    question = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
                    answer = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ""
                    
                    # Validate Q&A pair
                    if (question and answer and 
                        len(question) > 10 and len(answer) > 5 and
                        question.lower() not in ['item', 'question', 'nan'] and
                        answer.lower() not in ['answer', 'nan']):
                        
                        qa_pairs.append({
                            "question": question,
                            "answer": answer
                        })
            
        except Exception as e:
            main_logger.warning(f"MXNB style extraction failed: {str(e)}")
        
        return qa_pairs
    
    def _extract_by_column_names(self, df: pd.DataFrame) -> List[Dict]:
        """
        Extract Q&A by looking for 'Question' and 'Answer' column names
        """
        qa_pairs = []
        
        try:
            # Find question and answer columns
            question_col = None
            answer_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if any(q in col_lower for q in ['question', 'q', 'item', 'query']):
                    question_col = col
                elif any(a in col_lower for a in ['answer', 'a', 'response', 'reply']):
                    answer_col = col
            
            if question_col and answer_col:
                for i, row in df.iterrows():
                    question = str(row[question_col]).strip() if pd.notna(row[question_col]) else ""
                    answer = str(row[answer_col]).strip() if pd.notna(row[answer_col]) else ""
                    
                    if question and answer and len(question) > 10 and len(answer) > 5:
                        qa_pairs.append({
                            "question": question,
                            "answer": answer
                        })
        
        except Exception as e:
            main_logger.warning(f"Column name extraction failed: {str(e)}")
        
        return qa_pairs
    
    def _extract_by_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Extract Q&A by detecting question patterns and matching with answers
        """
        qa_pairs = []
        
        try:
            for i, row in df.iterrows():
                # Skip first row (usually headers)
                if i == 0:
                    continue
                
                question = None
                answer = None
                
                # Scan all columns
                for col in df.columns:
                    value = str(row[col]).strip()
                    
                    if pd.isna(row[col]) or not value or value == 'nan':
                        continue
                    
                    # Detect questions (must contain question words or ?)
                    if (any(q in value.lower() for q in ['what', 'how', 'why', 'when', 'where', 'who', 'do you', 'can you', 'will you', 'please']) or
                        '?' in value):
                        if not question or len(value) > len(question):
                            question = value
                    
                    # Detect answers (longer text, not headers)
                    elif (len(value) > 20 and 
                          not any(h in value.lower() for h in ['question', 'answer', 'item', 'dimension', 'category', 'owner'])):
                        if not answer or len(value) > len(answer):
                            answer = value
                
                # Validate and add
                if question and answer and len(question) > 10 and len(answer) > 10:
                    qa_pairs.append({
                        "question": question,
                        "answer": answer
                    })
        
        except Exception as e:
            main_logger.warning(f"Pattern-based extraction failed: {str(e)}")
        
        return qa_pairs
    
    def _clean_qa_pairs(self, qa_pairs: List[Dict]) -> List[Dict]:
        """
        Clean and deduplicate Q&A pairs
        """
        cleaned = []
        seen_questions = set()
        
        for qa in qa_pairs:
            # Clean text
            question = qa['question'].strip()
            answer = qa['answer'].strip()
            
            # Remove duplicates
            if question.lower() in seen_questions:
                continue
            
            # Validate quality
            if len(question) < 10 or len(answer) < 5:
                continue
            
            seen_questions.add(question.lower())
            cleaned.append({
                "question": question,
                "answer": answer
            })
        
        return cleaned
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding using text-embedding-3-large
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            log_error(main_logger, e, "generate_embedding", {"text": text[:50]})
            return None
    
    async def store_qa_with_embedding(self, qa_pair: Dict, source: str, category: str = "Uploaded Documents") -> bool:
        """
        Store Q&A pair in Supabase with embedding
        """
        try:
            # Generate embedding for the question
            embedding = await self.generate_embedding(qa_pair['question'])
            
            if not embedding:
                main_logger.warning(f"Failed to generate embedding for: {qa_pair['question'][:50]}")
                return False
            
            # Prepare data for Supabase
            data = {
                'question': qa_pair['question'],
                'answer': qa_pair['answer'],
                'category': category,
                'tags': json.dumps([source, "uploaded", "ai-extracted"]),
                'created_by': 'ai_processor',
                'is_active': True,
                'confidence_threshold': 0.1,
                'embedding': json.dumps(embedding)
            }
            
            # Insert into Supabase
            result = self.supabase.table('knowledge_base').insert(data).execute()
            
            if result.data:
                main_logger.info(f"Stored Q&A: {qa_pair['question'][:50]}...")
                return True
            else:
                main_logger.warning(f"Failed to store Q&A: {qa_pair['question'][:50]}")
                return False
                
        except Exception as e:
            log_error(main_logger, e, "store_qa_with_embedding", {"question": qa_pair['question'][:50]})
            return False
    
    async def process_document(self, file_path: str, file_type: str, filename: str) -> Dict:
        """
        Main processing pipeline:
        1. Extract Q&A pairs (AI or Excel parsing)
        2. Generate embeddings
        3. Store in Supabase
        """
        try:
            main_logger.info(f"Processing document: {filename} (type: {file_type})")
            
            # Step 1: Extract Q&A pairs based on file type
            if file_type in ['xlsx', 'xls']:
                qa_pairs = await self.extract_qa_from_excel(file_path, filename)
            else:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                qa_pairs = await self.extract_qa_from_text(content, filename)
            
            if not qa_pairs:
                return {
                    'success': False,
                    'message': 'No Q&A pairs found in document',
                    'qa_count': 0,
                    'stored_count': 0
                }
            
            # Step 2 & 3: Generate embeddings and store
            stored_count = 0
            for qa_pair in qa_pairs:
                if await self.store_qa_with_embedding(qa_pair, filename):
                    stored_count += 1
            
            main_logger.info(f"Processed {filename}: {stored_count}/{len(qa_pairs)} stored")
            
            return {
                'success': True,
                'message': f'Successfully processed {stored_count} Q&A pairs',
                'qa_count': len(qa_pairs),
                'stored_count': stored_count,
                'qa_pairs': qa_pairs[:5]  # Return first 5 for preview
            }
            
        except Exception as e:
            log_error(main_logger, e, "process_document", {"filename": filename})
            return {
                'success': False,
                'message': f'Error processing document: {str(e)}',
                'qa_count': 0,
                'stored_count': 0
            }
    
    async def batch_process_documents(self, file_paths: List[str], file_types: List[str], filenames: List[str]) -> Dict:
        """
        Process multiple documents at once
        """
        results = []
        total_stored = 0
        
        for file_path, file_type, filename in zip(file_paths, file_types, filenames):
            result = await self.process_document(file_path, file_type, filename)
            results.append(result)
            total_stored += result['stored_count']
        
        return {
            'success': True,
            'total_documents': len(file_paths),
            'total_qa_pairs': total_stored,
            'results': results
        }
