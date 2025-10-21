# Query schemas
"""
Request and response schemas for query operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """Query request schema"""
    query: str = Field(..., min_length=1, description="User query")
    top_k: int = Field(5, ge=1, le=50, description="Number of results")
    include_images: bool = Field(True, description="Include images in results")
    include_tables: bool = Field(True, description="Include tables in results")
    filters: Optional[dict] = Field(None, description="Search filters")

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
