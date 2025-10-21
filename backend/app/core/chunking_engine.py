# Semantic chunking engine
"""
Semantic text chunking with token-aware splitting.
Uses simple token counting for memory efficiency.
"""
from typing import List
from dataclasses import dataclass, field
import hashlib
from loguru import logger

@dataclass
class Chunk:
    """Semantic text chunk"""
    chunk_id: str
    content: str
    chunk_type: str  # 'text', 'image', 'table', 'composite'
    token_count: int
    metadata: dict = field(default_factory=dict)

class ChunkingEngine:
    """
    Semantic text chunking with token awareness.
    KISS principle: Simple token-based chunking without complex NLP models.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size  # Tokens per chunk
        self.chunk_overlap = chunk_overlap  # Tokens to overlap between chunks
        logger.debug(f"ChunkingEngine initialized: size={chunk_size}, overlap={chunk_overlap}")

    def chunk_text(self, text: str, document_id: str = "", metadata: dict = None) -> List[Chunk]:
        """
        Chunk text into overlapping semantic units.
        Uses simple token-based splitting without sentence boundaries.
        """
        if not text or len(text.strip()) < 10:
            return []

        metadata = metadata or {}
        chunks = []

        # Split text into words (tokens)
        words = text.split()

        # Calculate overlap in words (approximate)
        overlap_words = max(1, int((self.chunk_overlap / self.chunk_size) * len(words)))
        chunk_words = max(50, int((self.chunk_size / self.chunk_size) * len(words)))

        # Create overlapping chunks
        for i in range(0, len(words), chunk_words - overlap_words):
            chunk_words_slice = words[i:i + chunk_words]

            if len(chunk_words_slice) < 10:  # Skip very small chunks
                continue

            chunk_text = " ".join(chunk_words_slice)
            token_count = len(chunk_words_slice)

            chunk_id = self._generate_chunk_id(document_id, i, chunk_text)

            chunks.append(Chunk(
                chunk_id=chunk_id,
                content=chunk_text,
                chunk_type='text',
                token_count=token_count,
                metadata={
                    **metadata,
                    'chunk_start_word': i,
                    'chunk_end_word': min(i + chunk_words, len(words))
                }
            ))

        logger.debug(f"Created {len(chunks)} text chunks from {len(words)} words")
        return chunks

    def chunk_table(self, table_data: List[List[str]], document_id: str = "", metadata: dict = None) -> List[Chunk]:
        """
        Chunk structured table data.
        Creates chunks per row or group of rows depending on size.
        """
        if not table_data or len(table_data) < 2:
            return []

        metadata = metadata or {}
        chunks = []

        # Convert table to text format
        headers = table_data[0]
        header_text = " | ".join(headers)

        # Group rows into chunks
        rows_per_chunk = max(5, self.chunk_size // 50)  # Estimate based on chunk size

        for i in range(1, len(table_data), rows_per_chunk):
            row_slice = table_data[i:i + rows_per_chunk]

            # Format rows as text
            row_texts = []
            for row in row_slice:
                row_text = " | ".join(row)
                row_texts.append(row_text)

            chunk_text = header_text + "\n" + "\n".join(row_texts)
            token_count = len(chunk_text.split())

            chunk_id = self._generate_chunk_id(document_id, i, chunk_text)

            chunks.append(Chunk(
                chunk_id=chunk_id,
                content=chunk_text,
                chunk_type='table',
                token_count=token_count,
                metadata={
                    **metadata,
                    'table_start_row': i,
                    'table_end_row': min(i + rows_per_chunk, len(table_data))
                }
            ))

        logger.debug(f"Created {len(chunks)} table chunks from {len(table_data)} rows")
        return chunks

    def chunk_image(self, image_caption: str, image_id: str, metadata: dict = None) -> Chunk:
        """
        Create single chunk for image with its caption.
        Images are treated as atomic units.
        """
        if not image_caption or len(image_caption.strip()) < 3:
            return None

        metadata = metadata or {}
        token_count = len(image_caption.split())

        chunk = Chunk(
            chunk_id=f"img_{image_id}",
            content=image_caption,
            chunk_type='image',
            token_count=token_count,
            metadata={
                **metadata,
                'image_id': image_id
            }
        )

        logger.debug(f"Created image chunk for {image_id}")
        return chunk

    def chunk_composite(self, content: str, components: dict, document_id: str = "", metadata: dict = None) -> List[Chunk]:
        """
        Create chunks for mixed content (text + images + tables).
        Keeps related content together for better context.
        """
        metadata = metadata or {}
        chunks = []

        # Create single composite chunk
        chunk_id = self._generate_chunk_id(document_id, 0, content)
        token_count = len(content.split())

        chunks.append(Chunk(
            chunk_id=chunk_id,
            content=content,
            chunk_type='composite',
            token_count=token_count,
            metadata={
                **metadata,
                'components': list(components.keys())
            }
        ))

        return chunks

    def count_tokens(self, text: str) -> int:
        """
        Simple token count: split by whitespace.
        Approximation for speed without NLP libraries.
        """
        if not text:
            return 0

        # Count words as tokens (simple approximation)
        tokens = len(text.split())

        # Rough adjustment for subword tokens (BERT-style ~1.3x words)
        estimated_tokens = int(tokens * 1.3)

        return estimated_tokens

    def validate_chunk_boundaries(self, chunks: List[Chunk]) -> bool:
        """
        Validate chunk boundaries:
        - No empty chunks
        - Reasonable token count
        - IDs are unique
        """
        if not chunks:
            return True

        seen_ids = set()
        for chunk in chunks:
            # Check empty content
            if not chunk.content or len(chunk.content.strip()) < 3:
                logger.warning(f"Empty chunk detected: {chunk.chunk_id}")
                return False

            # Check duplicate IDs
            if chunk.chunk_id in seen_ids:
                logger.warning(f"Duplicate chunk ID: {chunk.chunk_id}")
                return False
            seen_ids.add(chunk.chunk_id)

            # Check token count
            if chunk.token_count < 5:
                logger.warning(f"Very small chunk: {chunk.chunk_id} ({chunk.token_count} tokens)")

        logger.debug(f"Validated {len(chunks)} chunks - all OK")
        return True

    def _generate_chunk_id(self, document_id: str, position: int, content: str) -> str:
        """Generate unique chunk ID from document, position, and content hash"""
        content_hash = hashlib.md5(content[:100].encode()).hexdigest()[:8]
        return f"{document_id}_{position}_{content_hash}".replace("/", "_")
