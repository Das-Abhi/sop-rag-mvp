# System Architecture - SOP RAG MVP

## Overview

The SOP RAG MVP is a multimodal retrieval-augmented generation system designed to understand and query complex PDF documents with text, images, and tables.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Frontend (React + TypeScript)                   │
│  - Chat Interface with real-time updates                               │
│  - Document library and viewer                                         │
│  - Processing progress tracking                                        │
│  - Citation visualization                                              │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │ WebSocket & REST APIs
┌──────────────────────────▼──────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ API Routes                                                      │  │
│  │ - /api/v1/query (RAG queries)                                   │  │
│  │ - /api/v1/documents (CRUD operations)                           │  │
│  │ - /api/v1/processing (Status monitoring)                        │  │
│  │ - /ws (WebSocket for real-time updates)                         │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ Core Services                                                   │  │
│  │ - Document Processor (orchestration)                            │  │
│  │ - Layout Analyzer (region detection)                            │  │
│  │ - Text/Image/Table Extraction                                   │  │
│  │ - Semantic Chunking                                             │  │
│  │ - Multi-Modal Embeddings                                        │  │
│  │ - Vision Service (Ollama integration)                           │  │
│  │ - RAG Engine (retrieval orchestration)                          │  │
│  │ - LLM Service (Ollama integration)                              │  │
│  │ - Cache Manager (Redis wrapper)                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└──────────────┬───────────────────────────────────────────────────────────┘
               │
        ┌──────┴─────────────────────────────────────────────────┐
        │                                                         │
        │                                                         │
┌───────▼───────┐  ┌─────────────────┐  ┌──────────────────────┐
│   PostgreSQL  │  │      Redis      │  │      MinIO (S3)      │
│   - Documents │  │  - Query Cache  │  │  - Binary Files      │
│   - Chunks    │  │  - Embeddings   │  │  - Images            │
│   - Metadata  │  │  - Sessions     │  │  - Backups           │
└───────────────┘  └─────────────────┘  └──────────────────────┘

        │
┌───────▼──────────────────────────────────────────────────────────┐
│              Celery Workers (Background Tasks)                   │
│  - Document processing pipeline                                  │
│  - Embedding generation                                          │
│  - Vector store indexing                                         │
│  - Result reranking                                              │
└───────────────────────────────────────────────────────────────────┘

        │
┌───────▼──────────────────────────────────────────────────────────┐
│         ChromaDB Vector Store                                    │
│  - text_chunks collection                                        │
│  - image_chunks collection                                       │
│  - table_chunks collection                                       │
│  - composite_chunks collection                                   │
└───────────────────────────────────────────────────────────────────┘

        │
┌───────▼──────────────────────────────────────────────────────────┐
│    External AI Services (via Ollama)                             │
│  - LLM: llama3.1:8b                                              │
│  - Vision: bakllava:7b, moondream2                               │
│  - Embeddings: BAAI/bge-base-en-v1.5                             │
│  - Reranker: BAAI/bge-reranker-base                              │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Document Upload & Processing

```
1. User uploads PDF
   ↓
2. Store in MinIO object storage
   ↓
3. Trigger Celery processing task
   ↓
4. Layout Analysis (pdfplumber + pymupdf)
   - Detect text blocks, images, tables
   - Generate regions with bounding boxes
   ↓
5. Extract Content
   - Text: Via pdfplumber
   - Images: Via pymupdf, store in MinIO
   - Tables: Multi-strategy extraction (pdfplumber, camelot, table-transformer)
   - OCR: PaddleOCR for scanned documents
   ↓
6. Semantic Chunking
   - Split text preserving semantics
   - Generate meaningful chunks
   - Maintain context
   ↓
7. Generate Embeddings
   - Text embeddings (BAAI/bge-base-en-v1.5)
   - Image embeddings (CLIP)
   - Table embeddings (structured)
   ↓
8. Store in Vector DB
   - Save chunks to ChromaDB
   - Index by type (text/image/table)
   - Enable similarity search
   ↓
9. Update Metadata
   - Store in PostgreSQL
   - Update processing status
```

### Query & Retrieval

```
1. User submits query
   ↓
2. Generate Query Embedding
   - Use same embedding model
   - Maintain consistency
   ↓
3. Retrieve Similar Chunks
   - Search ChromaDB collections
   - Return top-k results
   - Check Redis cache first
   ↓
4. Rerank Results
   - Use BAAI/bge-reranker-base
   - Score by relevance
   - Filter low scores
   ↓
5. Generate Response
   - Build context window
   - Format for LLM
   - Generate answer via llama3.1:8b
   ↓
6. Extract Citations
   - Map response to sources
   - Include page numbers
   - Add confidence scores
   ↓
7. Return to Frontend
   - Response text
   - Citations
   - Processing metadata
```

## Component Details

### Backend Modules

- **app/core/**: Core business logic
  - document_processor.py: Orchestrates full pipeline
  - layout_analyzer.py: PDF region detection
  - text_extractor.py: Text extraction
  - image_processor.py: Image extraction and analysis
  - table_extractor.py: Multi-strategy table extraction
  - chunking_engine.py: Semantic text chunking
  - embedding_service.py: Multi-modal embeddings
  - vision_service.py: Ollama vision models
  - rag_engine.py: RAG orchestration
  - reranker.py: Result reranking
  - llm_service.py: Ollama LLM integration
  - cache_manager.py: Redis caching
  - composite_assembler.py: Mixed content handling

- **app/services/**: External service integrations
  - vector_store.py: ChromaDB wrapper
  - object_storage.py: MinIO wrapper
  - websocket_manager.py: Real-time updates

- **app/api/v1/**: API routes
  - query.py: RAG query endpoint
  - documents.py: Document CRUD
  - processing.py: Status monitoring
  - websocket.py: WebSocket connection

- **app/tasks/**: Celery background tasks
  - document_tasks.py: Processing pipeline
  - embedding_tasks.py: Embedding generation
  - indexing_tasks.py: Vector store indexing

## Database Schema

### PostgreSQL Collections

- **documents**: Document metadata
- **chunks**: Text chunks with metadata
- **images**: Extracted images metadata
- **tables**: Table data and metadata
- **queries**: Query history and results
- **processing_tasks**: Background job tracking

### ChromaDB Collections

- **text_chunks**: Text content with embeddings
- **image_chunks**: Image descriptions with visual embeddings
- **table_chunks**: Table data with structured embeddings
- **composite_chunks**: Mixed content chunks

## Performance Optimization

### Caching Strategy
- Query results cached in Redis (1 hour TTL)
- Embeddings cached (persistent)
- Model responses cached

### Retrieval Optimization
- Top-k retrieval limited to 50 results
- Reranking applied to top-k
- Early filtering by score threshold

### Processing Optimization
- Batch embedding generation
- Parallel table extraction strategies
- Incremental indexing

## Scalability Considerations

- Horizontal scaling via Celery workers
- Load balancing for API servers
- Read replicas for PostgreSQL
- Distributed caching with Redis cluster
- Vector DB clustering support

## Security

- Environment-based configuration
- Database connection pooling
- Input validation on all endpoints
- Rate limiting (TODO: implement)
- CORS configuration
- WebSocket authentication (TODO: implement)

## Monitoring & Logging

- Structured JSON logging (Loguru)
- Processing progress tracking
- Query performance metrics
- Error tracking and reporting
- Health check endpoints

## Future Enhancements

- Multi-language support
- Fine-tuning on domain-specific data
- Advanced caching strategies
- Distributed processing
- Real-time collaboration
- Advanced analytics
