# Enhanced Document Processing for Vector Search

## Current System Integration

Your document processing logic is excellent! Here's how we can enhance it for vector search:

### 1. **Chunking Strategy**
Instead of storing entire documents as single entries, we should chunk them:

```javascript
const chunkDocument = (content, filename, chunkSize = 1000) => {
  const chunks = [];
  const lines = content.split('\n');
  let currentChunk = '';
  
  for (const line of lines) {
    if (currentChunk.length + line.length > chunkSize) {
      chunks.push({
        content: currentChunk.trim(),
        source: filename,
        chunk_id: chunks.length + 1
      });
      currentChunk = line;
    } else {
      currentChunk += '\n' + line;
    }
  }
  
  if (currentChunk.trim()) {
    chunks.push({
      content: currentChunk.trim(),
      source: filename,
      chunk_id: chunks.length + 1
    });
  }
  
  return chunks;
};
```

### 2. **Enhanced File Processing**
```javascript
const processFileForVectorSearch = async (file) => {
  const ext = file.name.split('.').pop().toLowerCase();
  let content = '';
  
  if (ext === 'txt' || ext === 'md' || ext === 'csv') {
    content = await file.text();
  } else if (ext === 'xlsx' || ext === 'xls') {
    const buffer = await file.arrayBuffer();
    const wb = XLSX.read(buffer);
    wb.SheetNames.forEach(name => {
      content += '\n--- ' + name + ' ---\n' + XLSX.utils.sheet_to_csv(wb.Sheets[name]);
    });
  }
  
  // Chunk the content
  const chunks = chunkDocument(content, file.name);
  
  // Generate embeddings for each chunk
  const chunksWithEmbeddings = await Promise.all(
    chunks.map(async (chunk) => {
      const embedding = await generateEmbedding(chunk.content);
      return {
        ...chunk,
        embedding: embedding,
        metadata: {
          file_type: ext,
          file_size: file.size,
          upload_date: new Date().toISOString()
        }
      };
    })
  );
  
  return chunksWithEmbeddings;
};
```

### 3. **Vector Search Integration**
```javascript
const searchWithVectors = async (query, topK = 5) => {
  // Generate embedding for the query
  const queryEmbedding = await generateEmbedding(query);
  
  // Search in vector database (Supabase with pgvector)
  const { data, error } = await supabase.rpc('match_documents', {
    query_embedding: queryEmbedding,
    match_threshold: 0.7,
    match_count: topK
  });
  
  return data;
};
```

## Database Schema for Vector Search

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filename TEXT NOT NULL,
  content TEXT NOT NULL,
  chunk_id INTEGER,
  source TEXT,
  file_type TEXT,
  file_size BIGINT,
  upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  embedding VECTOR(1536), -- OpenAI ada-002 embedding size
  metadata JSONB
);

-- Create index for vector search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(1536),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  source TEXT,
  similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    documents.id,
    documents.content,
    documents.source,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
$$;
```

## Enhanced Knowledge Base Service

```python
class VectorKnowledgeBaseService:
    def __init__(self, db: Session, openai_client):
        self.db = db
        self.openai_client = openai_client
    
    async def add_document(self, filename: str, content: str, file_type: str):
        """Add document with vector embeddings"""
        chunks = self._chunk_content(content, filename)
        
        for chunk in chunks:
            # Generate embedding
            embedding = await self._generate_embedding(chunk['content'])
            
            # Store in database
            doc = Document(
                filename=filename,
                content=chunk['content'],
                chunk_id=chunk['chunk_id'],
                source=filename,
                file_type=file_type,
                embedding=embedding
            )
            self.db.add(doc)
        
        self.db.commit()
    
    async def search_similar(self, query: str, top_k: int = 5):
        """Search for similar content using vector similarity"""
        query_embedding = await self._generate_embedding(query)
        
        # Use Supabase vector search
        results = await self._vector_search(query_embedding, top_k)
        return results
    
    async def _generate_embedding(self, text: str):
        """Generate OpenAI embedding"""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
```

## Benefits of This Approach

### 1. **Better Question Matching**
- **Semantic Understanding**: Finds conceptually similar content
- **Context Awareness**: Understands question intent, not just keywords
- **Multi-language Support**: Works with different languages

### 2. **Improved Document Processing**
- **Chunking**: Better handling of large documents
- **Metadata**: Rich context about document sources
- **Versioning**: Track document updates over time

### 3. **Enhanced Search Capabilities**
- **Similarity Scoring**: Rank results by relevance
- **Hybrid Search**: Combine vector search with keyword search
- **Real-time Updates**: Add new documents without rebuilding index

## Implementation Plan

### Phase 1: Supabase Setup
1. Create Supabase project
2. Enable vector extension
3. Set up database schema
4. Migrate existing data

### Phase 2: Vector Search Implementation
1. Implement embedding generation
2. Add document chunking
3. Create vector search functions
4. Update API endpoints

### Phase 3: Enhanced Document Processing
1. Integrate your file processing logic
2. Add chunking and embedding generation
3. Implement hybrid search (vector + keyword)
4. Add metadata tracking

### Phase 4: Testing and Optimization
1. Test with various document types
2. Optimize chunk sizes and similarity thresholds
3. Performance testing
4. User experience improvements

## Questions for You

1. **Chunk Size**: What chunk size do you prefer? (500, 1000, 1500 characters?)
2. **Similarity Threshold**: How strict should the matching be? (0.7, 0.8, 0.9?)
3. **Hybrid Search**: Should we combine vector search with keyword search?
4. **Document Types**: Any specific document types you want to prioritize?
5. **Metadata**: What additional metadata would be useful?

Your document processing logic is solid - we just need to enhance it with vector embeddings and chunking for better AI-powered search!
