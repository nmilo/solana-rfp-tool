from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
import openai
import numpy as np
from app.models.database import KnowledgeBase
from app.core.config import settings
from app.core.logger import main_logger, log_error
import json

class VectorSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-large"  # Latest and most powerful model
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate OpenAI embedding for text"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            log_error(main_logger, e, "generate_embedding", {"text": text[:100]})
            return []
    
    async def add_document_with_embedding(self, question: str, answer: str, category: str = None, tags: List[str] = None):
        """Add document with vector embedding"""
        try:
            # Generate embedding for question
            embedding = await self.generate_embedding(question)
            
            if not embedding:
                return None
            
            # Create knowledge base entry
            kb_entry = KnowledgeBase(
                question=question,
                answer=answer,
                category=category,
                tags=json.dumps(tags or []),
                embedding=json.dumps(embedding),  # Store as JSON string
                is_active=True
            )
            
            self.db.add(kb_entry)
            self.db.commit()
            
            main_logger.info(f"Added document with embedding: {question[:50]}...")
            return kb_entry
            
        except Exception as e:
            log_error(main_logger, e, "add_document_with_embedding", {"question": question[:50]})
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            log_error(main_logger, e, "cosine_similarity", {})
            return 0.0
    
    async def search_similar_documents(self, query: str, top_k: int = 5, min_similarity: float = 0.7) -> List[Dict]:
        """Search for similar documents using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Get all active entries with embeddings
            entries = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.is_active == True,
                KnowledgeBase.embedding.isnot(None)
            ).all()
            
            # Calculate similarities
            similarities = []
            for entry in entries:
                try:
                    entry_embedding = json.loads(entry.embedding)
                    similarity = self.cosine_similarity(query_embedding, entry_embedding)
                    
                    if similarity >= min_similarity:
                        similarities.append({
                            "id": str(entry.id),
                            "question": entry.question,
                            "answer": entry.answer,
                            "similarity": similarity,
                            "category": entry.category,
                            "tags": entry.get_tags(),
                            "match_type": "vector"
                        })
                except Exception as e:
                    continue
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            log_error(main_logger, e, "search_similar_documents", {"query": query[:50]})
            return []
    
    async def get_best_vector_match(self, query: str, min_similarity: float = 0.7) -> Optional[Dict]:
        """Get the best matching document using vector search"""
        matches = await self.search_similar_documents(query, top_k=1, min_similarity=min_similarity)
        return matches[0] if matches else None
    
    async def add_existing_knowledge_base_embeddings(self):
        """Add embeddings to existing knowledge base entries"""
        try:
            entries = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.is_active == True,
                KnowledgeBase.embedding.is_(None)
            ).all()
            
            main_logger.info(f"Adding embeddings to {len(entries)} existing entries")
            
            for entry in entries:
                embedding = await self.generate_embedding(entry.question)
                if embedding:
                    entry.embedding = json.dumps(embedding)
                    self.db.commit()
                    main_logger.info(f"Added embedding for: {entry.question[:50]}...")
            
            main_logger.info("Finished adding embeddings to existing entries")
            
        except Exception as e:
            log_error(main_logger, e, "add_existing_knowledge_base_embeddings", {})
    
    def chunk_document(self, content: str, filename: str, chunk_size: int = 1000) -> List[Dict]:
        """Chunk document content for better vector search"""
        chunks = []
        lines = content.split('\n')
        current_chunk = ''
        chunk_id = 1
        
        for line in lines:
            if len(current_chunk) + len(line) > chunk_size and current_chunk:
                chunks.append({
                    'content': current_chunk.strip(),
                    'source': filename,
                    'chunk_id': chunk_id
                })
                current_chunk = line
                chunk_id += 1
            else:
                current_chunk += '\n' + line if current_chunk else line
        
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'source': filename,
                'chunk_id': chunk_id
            })
        
        return chunks
