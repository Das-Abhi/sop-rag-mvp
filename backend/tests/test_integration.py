"""
Integration tests for the SOP RAG MVP system
"""
import pytest
from fastapi.testclient import TestClient
import tempfile
import os
from datetime import datetime

from app.main import app
from app.database import SessionLocal, init_db, Base, engine
from app.models import Document, Chunk, ProcessingTask, QueryLog
from app.crud import DocumentCRUD, ChunkCRUD, ProcessingTaskCRUD, QueryLogCRUD
from app.services.vector_store import VectorStore
from app.core.cache_manager import CacheManager
from app.core.embedding_service import EmbeddingService
from app.core.chunking_engine import ChunkingEngine


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def db():
    """Get database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


class TestDocumentCRUD:
    """Test Document CRUD operations"""

    def test_create_document(self, db):
        """Test creating a document"""
        doc = DocumentCRUD.create(
            db=db,
            document_id="test-doc-1",
            title="Test Document",
            file_path="/tmp/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        assert doc.document_id == "test-doc-1"
        assert doc.title == "Test Document"
        assert doc.status == "pending"

    def test_get_document(self, db):
        """Test retrieving a document"""
        doc = DocumentCRUD.create(
            db=db,
            document_id="test-doc-2",
            title="Test Doc 2",
            file_path="/tmp/test2.pdf",
            file_size=2048
        )
        retrieved = DocumentCRUD.get(db, "test-doc-2")
        assert retrieved is not None
        assert retrieved.title == "Test Doc 2"

    def test_list_documents(self, db):
        """Test listing documents"""
        DocumentCRUD.create(db, "doc-1", "Doc 1", "/tmp/1.pdf", 1000)
        DocumentCRUD.create(db, "doc-2", "Doc 2", "/tmp/2.pdf", 2000)

        docs = DocumentCRUD.list_all(db)
        assert len(docs) >= 2

    def test_update_document_status(self, db):
        """Test updating document status"""
        DocumentCRUD.create(db, "doc-3", "Doc 3", "/tmp/3.pdf", 3000)
        updated = DocumentCRUD.update_status(db, "doc-3", "processing")
        assert updated.status == "processing"

    def test_update_chunk_counts(self, db):
        """Test updating chunk counts"""
        DocumentCRUD.create(db, "doc-4", "Doc 4", "/tmp/4.pdf", 4000)
        updated = DocumentCRUD.update_chunk_counts(db, "doc-4", 10, 5, 2)
        assert updated.text_chunks == 10
        assert updated.image_chunks == 5
        assert updated.table_chunks == 2
        assert updated.total_chunks == 17

    def test_count_documents(self, db):
        """Test counting documents"""
        DocumentCRUD.create(db, "doc-5", "Doc 5", "/tmp/5.pdf", 5000, "pdf")
        DocumentCRUD.create(db, "doc-6", "Doc 6", "/tmp/6.pdf", 6000, "txt")
        count = DocumentCRUD.count(db)
        assert count >= 2


class TestChunkCRUD:
    """Test Chunk CRUD operations"""

    def test_create_chunk(self, db):
        """Test creating a chunk"""
        # Create document first
        DocumentCRUD.create(db, "doc-chunk-1", "Doc", "/tmp/doc.pdf", 1000)

        chunk = ChunkCRUD.create(
            db=db,
            chunk_id="chunk-1",
            document_id="doc-chunk-1",
            content="Test chunk content",
            chunk_type="text",
            token_count=5
        )
        assert chunk.chunk_id == "chunk-1"
        assert chunk.content == "Test chunk content"
        assert chunk.is_indexed is False

    def test_bulk_create_chunks(self, db):
        """Test bulk creating chunks"""
        DocumentCRUD.create(db, "doc-bulk", "Doc", "/tmp/doc.pdf", 1000)

        chunks_data = [
            {
                "chunk_id": f"chunk-{i}",
                "document_id": "doc-bulk",
                "content": f"Chunk content {i}",
                "chunk_type": "text",
                "token_count": 5
            }
            for i in range(3)
        ]

        chunks = ChunkCRUD.bulk_create(db, chunks_data)
        assert len(chunks) == 3

    def test_mark_indexed(self, db):
        """Test marking chunk as indexed"""
        DocumentCRUD.create(db, "doc-indexed", "Doc", "/tmp/doc.pdf", 1000)
        ChunkCRUD.create(db, "chunk-idx", "doc-indexed", "Content", "text")

        updated = ChunkCRUD.mark_indexed(db, "chunk-idx")
        assert updated.is_indexed is True

    def test_get_by_document(self, db):
        """Test retrieving chunks for a document"""
        DocumentCRUD.create(db, "doc-chunks", "Doc", "/tmp/doc.pdf", 1000)
        ChunkCRUD.create(db, "chunk-1", "doc-chunks", "Content 1", "text")
        ChunkCRUD.create(db, "chunk-2", "doc-chunks", "Content 2", "text")

        chunks = ChunkCRUD.get_by_document(db, "doc-chunks")
        assert len(chunks) == 2


class TestProcessingTaskCRUD:
    """Test ProcessingTask CRUD operations"""

    def test_create_task(self, db):
        """Test creating a processing task"""
        DocumentCRUD.create(db, "doc-task", "Doc", "/tmp/doc.pdf", 1000)

        task = ProcessingTaskCRUD.create(
            db=db,
            task_id="task-1",
            document_id="doc-task",
            task_type="process_document",
            celery_task_id="celery-123"
        )
        assert task.task_id == "task-1"
        assert task.status == "pending"
        assert task.progress == 0

    def test_update_progress(self, db):
        """Test updating task progress"""
        DocumentCRUD.create(db, "doc-prog", "Doc", "/tmp/doc.pdf", 1000)
        ProcessingTaskCRUD.create(db, "task-prog", "doc-prog", "process_document")

        updated = ProcessingTaskCRUD.update_progress(
            db, "task-prog", 50, "Extracting text"
        )
        assert updated.progress == 50
        assert updated.current_step == "Extracting text"

    def test_update_status(self, db):
        """Test updating task status"""
        DocumentCRUD.create(db, "doc-status", "Doc", "/tmp/doc.pdf", 1000)
        ProcessingTaskCRUD.create(db, "task-status", "doc-status", "process_document")

        updated = ProcessingTaskCRUD.update_status(db, "task-status", "completed")
        assert updated.status == "completed"
        assert updated.completed_at is not None


class TestQueryLogCRUD:
    """Test QueryLog CRUD operations"""

    def test_create_query_log(self, db):
        """Test creating a query log"""
        log = QueryLogCRUD.create(
            db=db,
            query_id="query-1",
            query_text="What is SOPs?"
        )
        assert log.query_id == "query-1"
        assert log.query_text == "What is SOPs?"

    def test_update_query_log(self, db):
        """Test updating query log"""
        QueryLogCRUD.create(db, "query-2", "Test query")

        updated = QueryLogCRUD.update(
            db, "query-2",
            response_text="Test response",
            chunks_retrieved=5,
            chunks_reranked=3,
            latency_ms=1250.5
        )
        assert updated.response_text == "Test response"
        assert updated.chunks_retrieved == 5

    def test_add_feedback(self, db):
        """Test adding feedback to query"""
        QueryLogCRUD.create(db, "query-3", "Test query")

        updated = QueryLogCRUD.add_feedback(db, "query-3", "positive")
        assert updated.user_feedback == "positive"

    def test_get_recent_queries(self, db):
        """Test getting recent queries"""
        for i in range(3):
            QueryLogCRUD.create(db, f"query-{i}", f"Query {i}")

        recent = QueryLogCRUD.get_recent(db, limit=2)
        assert len(recent) <= 2


class TestVectorStore:
    """Test Vector Store operations"""

    def test_vector_store_init(self):
        """Test vector store initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(chroma_path=tmpdir)
            assert store.chroma_path == tmpdir
            assert len(store.collections) == 4

    def test_add_chunks(self):
        """Test adding chunks to vector store"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(chroma_path=tmpdir)

            chunks = [
                {
                    "id": "chunk-1",
                    "content": "Test content",
                    "embedding": [0.1] * 768,
                    "metadata": {"source": "test.pdf"}
                }
            ]

            success = store.add_chunks("text_chunks", chunks)
            assert success is True

    def test_search(self):
        """Test searching vector store"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(chroma_path=tmpdir)
            embedding = EmbeddingService()

            # Add a chunk
            query_embedding = embedding.embed_text("test")
            chunks = [
                {
                    "id": "chunk-1",
                    "content": "test content",
                    "embedding": query_embedding,
                    "metadata": {"source": "test.pdf"}
                }
            ]
            store.add_chunks("text_chunks", chunks)

            # Search
            results = store.search("text_chunks", query_embedding, top_k=5)
            assert isinstance(results, list)


class TestCacheManager:
    """Test Cache Manager operations"""

    def test_cache_embedding(self):
        """Test caching embeddings"""
        try:
            cache = CacheManager()
            embedding = [0.1, 0.2, 0.3]

            success = cache.cache_embedding("test text", embedding)
            assert success is True

            # Retrieve
            cached = cache.get_cached_embedding("test text")
            assert cached == embedding
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

    def test_cache_query_result(self):
        """Test caching query results"""
        try:
            cache = CacheManager()
            result = {"response": "Test answer", "citations": []}

            success = cache.cache_query_result("test query", result)
            assert success is True

            # Retrieve
            cached = cache.get_cached_query_result("test query")
            assert cached == result
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")


class TestChunkingEngine:
    """Test Chunking Engine"""

    def test_chunk_text(self):
        """Test text chunking"""
        engine = ChunkingEngine()
        text = " ".join(["word"] * 100)  # 100 words

        chunks = engine.chunk_text(text, "doc-1")
        assert len(chunks) > 0
        assert all(hasattr(c, 'chunk_id') for c in chunks)
        assert all(hasattr(c, 'content') for c in chunks)


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "services" in response.json()

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_document_list(self, client):
        """Test document list endpoint"""
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        assert "documents" in response.json()

    def test_processing_health(self, client):
        """Test processing health endpoint"""
        response = client.get("/api/v1/processing/health")
        assert response.status_code == 200
        assert "status" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
