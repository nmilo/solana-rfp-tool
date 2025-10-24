from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from app.models.database import KnowledgeBase
from app.models.schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate

class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.vectorizer = None
        self.X = None
        self.corpus = None
        self.kb_items = []
        self._rebuild_index()
    
    def _rebuild_index(self):
        """Rebuild TF-IDF index when knowledge base changes"""
        self.kb_items = self.get_all_active_entries()
        if not self.kb_items:
            return
            
        corpus = [
            self._normalize_text(
                item.question + " " + item.answer + " " + " ".join(item.get_tags())
            ) 
            for item in self.kb_items
        ]
        
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        self.X = self.vectorizer.fit_transform(corpus)
        self.corpus = corpus
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing - from your existing autoresponder.py"""
        text = text.lower()
        text = re.sub(r"[^\w\s\-\.]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    
    def get_all_active_entries(self) -> List[KnowledgeBase]:
        """Get all active knowledge base entries"""
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).all()
    
    def search_answers(self, question: str, min_confidence: float = 0.1) -> List[Dict]:
        """Search knowledge base for answers to a question with priority system"""
        if not self.kb_items:
            return []
        
        # Priority 1: Look for exact question matches first
        exact_matches = []
        for kb_item in self.kb_items:
            if self._is_exact_match(question, kb_item.question):
                exact_matches.append({
                    "id": kb_item.id,
                    "question": kb_item.question,
                    "answer": kb_item.answer,
                    "confidence": 1.0,  # Exact match gets highest confidence
                    "tags": kb_item.get_tags(),
                    "category": kb_item.category,
                    "match_type": "exact"
                })
        
        if exact_matches:
            # Return exact matches first, sorted by question length (most specific first)
            exact_matches.sort(key=lambda x: len(x["question"]), reverse=True)
            return exact_matches
        
        # Priority 2: If no exact match, use semantic search
        if not self.vectorizer:
            return []
        
        # Normalize question
        qn = self._normalize_text(question)
        qv = self.vectorizer.transform([qn])
        
        # Calculate similarities
        similarities = cosine_similarity(qv, self.X)[0]
        
        # Get matches above threshold
        matches = []
        for i, score in enumerate(similarities):
            if score >= min_confidence:
                kb_item = self.kb_items[i]
                matches.append({
                    "id": kb_item.id,
                    "question": kb_item.question,
                    "answer": kb_item.answer,
                    "confidence": float(score),
                    "tags": kb_item.get_tags(),
                    "category": kb_item.category,
                    "match_type": "semantic"
                })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches
    
    def _is_exact_match(self, question1: str, question2: str) -> bool:
        """Check if two questions are exact matches (case-insensitive, normalized)"""
        q1_norm = self._normalize_text(question1).lower()
        q2_norm = self._normalize_text(question2).lower()
        
        # Exact match
        if q1_norm == q2_norm:
            return True
        
        # Check if one is contained in the other (for partial matches)
        if len(q1_norm) > 20 and len(q2_norm) > 20:
            if q1_norm in q2_norm or q2_norm in q1_norm:
                return True
        
        return False
    
    def get_best_answer(self, question: str, min_confidence: float = 0.1) -> Optional[Dict]:
        """Get the best matching answer for a question"""
        matches = self.search_answers(question, min_confidence)
        return matches[0] if matches else None
    
    async def get_answer_with_ai_fallback(self, question: str, min_confidence: float = 0.1) -> Dict:
        """Get answer with smart AI fallback if no knowledge base match found"""
        # First try knowledge base search
        matches = self.search_answers(question, min_confidence)
        
        if matches:
            # Return the best match from knowledge base
            best_match = matches[0]
            return {
                "question": question,
                "answer": best_match["answer"],
                "confidence": best_match["confidence"],
                "source_id": best_match["id"],
                "source_question": best_match["question"],
                "match_type": best_match.get("match_type", "semantic"),
                "source": "knowledge_base",
                "source_label": "KB Match" if best_match.get("match_type") == "exact" else "KB Similar"
            }
        
        # If no knowledge base match, try broader search with lower confidence
        broader_matches = self.search_answers(question, min_confidence=0.05)
        if broader_matches:
            best_match = broader_matches[0]
            return {
                "question": question,
                "answer": best_match["answer"],
                "confidence": best_match["confidence"],
                "source_id": best_match["id"],
                "source_question": best_match["question"],
                "match_type": "semantic",
                "source": "knowledge_base",
                "source_label": "KB Similar"
            }
        
        # If still no match, decide whether to use AI or return no answer
        if self._should_use_ai_for_question(question):
            ai_answer = await self._generate_ai_answer(question)
            return {
                "question": question,
                "answer": ai_answer,
                "confidence": 0.8,
                "source_id": None,
                "source_question": None,
                "match_type": "ai_generated",
                "source": "ai",
                "source_label": "AI Generated"
            }
        else:
            return {
                "question": question,
                "answer": "No answer found in knowledge base for this question.",
                "confidence": 0.0,
                "source_id": None,
                "source_question": None,
                "match_type": "no_answer",
                "source": "none",
                "source_label": "No Answer"
            }
    
    def _should_use_ai_for_question(self, question: str) -> bool:
        """Determine if AI should be used for this question"""
        question_lower = question.lower()
        
        # Questions that are clearly about Solana/blockchain should get AI answers
        solana_keywords = [
            'solana', 'blockchain', 'crypto', 'defi', 'nft', 'smart contract',
            'validator', 'consensus', 'transaction', 'block', 'network',
            'token', 'wallet', 'staking', 'governance', 'security',
            'scalability', 'throughput', 'latency', 'fee', 'cost',
            'developer', 'sdk', 'api', 'documentation', 'testnet',
            'mainnet', 'rpc', 'node', 'bridge', 'oracle'
        ]
        
        # Check if question contains Solana/blockchain related terms
        if any(keyword in question_lower for keyword in solana_keywords):
            return True
        
        # Check if it's a technical question
        technical_indicators = [
            'how does', 'how do', 'what is', 'what are', 'how to',
            'can you', 'does solana', 'is solana', 'will solana',
            'does the', 'is the', 'what the', 'how the'
        ]
        
        if any(indicator in question_lower for indicator in technical_indicators):
            return True
        
        # If it's a very specific question that might not be in KB, use AI
        if len(question) > 30 and ('?' in question or any(word in question_lower for word in ['please', 'provide', 'explain', 'describe'])):
            return True
        
        return False
    
    async def _generate_ai_answer(self, question: str) -> str:
        """Generate an AI answer for a question not in knowledge base"""
        try:
            import openai
            from app.core.config import settings
            
            if not settings.OPENAI_API_KEY:
                return "I don't have enough information to answer this question. Please consult the Solana documentation or contact our technical team for assistance."
            
            openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            prompt = f"""
            You are a Solana blockchain expert responding to RFP questions. 
            Provide a comprehensive, professional answer to the following question based on Solana's capabilities and features.
            The answer should be suitable for a Request for Proposal (RFP) response.
            
            Question: {question}
            
            Provide a detailed answer covering:
            1. Solana's specific capabilities related to this question
            2. Technical details and specifications
            3. Benefits and advantages
            4. Real-world examples or use cases where applicable
            5. Any relevant statistics or metrics
            
            Answer:
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Add source attribution
            answer += "\n\n[This answer was generated using AI based on Solana blockchain knowledge.]"
            
            return answer
            
        except Exception as e:
            return f"I don't have enough information to answer this question. Please consult the Solana documentation or contact our technical team for assistance. Error: {str(e)}"
    
    def add_entry(self, entry_data: KnowledgeBaseCreate, created_by: str = "admin") -> Dict:
        """Add new knowledge base entry"""
        # Check for duplicates
        existing = self.search_answers(entry_data.question, min_confidence=0.8)
        if existing:
            raise ValueError("Similar question already exists in knowledge base")
        
        # Add to database with all required fields
        kb_entry = KnowledgeBase(
            question=entry_data.question,
            answer=entry_data.answer,
            category=entry_data.category,
            confidence_threshold=0.1,  # Default confidence threshold
            is_active=True,  # Default to active
            created_by=created_by,
            last_modified_by=created_by
        )
        kb_entry.set_tags(entry_data.tags or [])
        self.db.add(kb_entry)
        self.db.commit()
        self.db.refresh(kb_entry)
        
        # Rebuild index
        self._rebuild_index()
        
        return {
            "id": kb_entry.id,
            "question": kb_entry.question,
            "answer": kb_entry.answer,
            "tags": kb_entry.get_tags(),
            "category": kb_entry.category,
            "confidence_threshold": kb_entry.confidence_threshold,
            "is_active": kb_entry.is_active,
            "created_at": kb_entry.created_at.isoformat(),
            "updated_at": kb_entry.updated_at.isoformat(),
            "created_by": kb_entry.created_by,
            "last_modified_by": kb_entry.last_modified_by
        }
    
    def update_entry(self, entry_id: str, update_data: KnowledgeBaseUpdate, modified_by: str = "admin") -> Dict:
        """Update knowledge base entry"""
        kb_entry = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
        if not kb_entry:
            raise ValueError("Knowledge base entry not found")
        
        if update_data.question is not None:
            kb_entry.question = update_data.question
        if update_data.answer is not None:
            kb_entry.answer = update_data.answer
        if update_data.tags is not None:
            kb_entry.set_tags(update_data.tags)
        if update_data.category is not None:
            kb_entry.category = update_data.category
        
        kb_entry.last_modified_by = modified_by
        self.db.commit()
        self.db.refresh(kb_entry)
        
        # Rebuild index
        self._rebuild_index()
        
        return {
            "id": kb_entry.id,
            "question": kb_entry.question,
            "answer": kb_entry.answer,
            "tags": kb_entry.tags,
            "category": kb_entry.category
        }
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete knowledge base entry"""
        kb_entry = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
        if not kb_entry:
            return False
        
        self.db.delete(kb_entry)
        self.db.commit()
        
        # Rebuild index
        self._rebuild_index()
        return True
    
    def get_all_entries(self, category: str = None, tags: List[str] = None) -> List[Dict]:
        """Get all knowledge base entries with optional filtering"""
        query = self.db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
        
        if category:
            query = query.filter(KnowledgeBase.category == category)
        
        if tags:
            # For SQLite, we'll filter in Python since we can't use array operations
            pass
        
        entries = query.order_by(KnowledgeBase.created_at.desc()).all()
        
        result = [
            {
                "id": entry.id,
                "question": entry.question,
                "answer": entry.answer,
                "tags": entry.get_tags(),
                "category": entry.category,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
                "created_by": entry.created_by,
                "last_modified_by": entry.last_modified_by
            }
            for entry in entries
        ]
        
        # Filter by tags in Python for SQLite compatibility
        if tags:
            result = [entry for entry in result if any(tag in entry["tags"] for tag in tags)]
        
        return result
    
    def import_from_json(self, json_data: List[Dict], created_by: str = "admin") -> int:
        """Import knowledge base entries from JSON (like your existing rfp_kb.json)"""
        imported_count = 0
        
        for item in json_data:
            try:
                # Check if entry already exists
                existing = self.search_answers(item.get("question", ""), min_confidence=0.8)
                if existing:
                    continue
                
                kb_entry = KnowledgeBase(
                    question=item.get("question", ""),
                    answer=item.get("answer", ""),
                    category=item.get("category"),
                    confidence_threshold=0.1,  # Default confidence threshold
                    is_active=True,  # Default to active
                    created_by=created_by,
                    last_modified_by=created_by
                )
                kb_entry.set_tags(item.get("tags", []))
                self.db.add(kb_entry)
                imported_count += 1
            except Exception as e:
                print(f"Error importing entry: {e}")
                continue
        
        self.db.commit()
        self._rebuild_index()
        return imported_count
