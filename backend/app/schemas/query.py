# Query schemas
"""
Request and response schemas for query operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """Query request schema"""
    query: Optional[str] = Field(None, min_length=1, description="User query")
    query_text: Optional[str] = Field(None, min_length=1, description="User query (alternative field)")
    document_ids: Optional[List[str]] = Field(None, description="Document IDs to query")
    top_k: int = Field(5, ge=1, le=50, description="Number of results")
    rerank_top_k: Optional[int] = Field(None, ge=1, le=50, description="Reranking top k")
    include_images: bool = Field(True, description="Include images in results")
    include_tables: bool = Field(True, description="Include tables in results")
    filters: Optional[dict] = Field(None, description="Search filters")
    system_prompt: Optional[str] = Field(None, description="System prompt for LLM")

    def __init__(self, **data):
        # Support both 'query' and 'query_text' fields
        if 'query_text' in data and 'query' not in data:
            data['query'] = data.pop('query_text')
        super().__init__(**data)

class Citation(BaseModel):
    """Citation information"""
    chunk_id: str
    source: str
    page: int
    confidence: float
    text: str

class QueryResponse(BaseModel):
    """Query response schema"""
    query: str
    response: str
    citations: List[Citation]
    processing_time: float
    model: str

class SearchResult(BaseModel):
    """Individual search result"""
    result_id: str
    content: str
    content_type: str  # 'text', 'image', 'table'
    confidence: float
    source: str
    page: int

class SearchResponse(BaseModel):
    """Search response schema"""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time: float
