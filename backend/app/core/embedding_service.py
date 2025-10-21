# Embedding service
"""
Multi-modal embedding generation for text, images, and tables.
Uses sentence-transformers for text and CLIP for images.
"""
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger
import os

class EmbeddingService:
    """
    Generates embeddings for different content types.
    KISS principle: Use proven pre-trained models without fine-tuning.
    """

    def __init__(self, text_model: str = "BAAI/bge-base-en-v1.5"):
        self.text_model_name = text_model
        self.embedding_dim = 768

        # Initialize text encoder
        try:
            self.text_encoder = SentenceTransformer(
                text_model,
                cache_folder=os.environ.get("HF_HOME", "./cache/huggingface")
            )
            logger.info(f"Text encoder initialized: {text_model}")
        except Exception as e:
            logger.error(f"Failed to initialize text encoder: {e}")
            self.text_encoder = None

        # Initialize image encoder (CLIP)
        try:
            from PIL import Image
            from transformers import CLIPProcessor, CLIPModel

            self.clip_model_name = "openai/clip-vit-base-patch32"
            self.clip_model = CLIPModel.from_pretrained(
                self.clip_model_name,
                cache_dir=os.environ.get("HF_HOME", "./cache/huggingface")
            )
            self.clip_processor = CLIPProcessor.from_pretrained(
                self.clip_model_name,
                cache_dir=os.environ.get("HF_HOME", "./cache/huggingface")
            )
            logger.info("CLIP image encoder initialized")
        except Exception as e:
            logger.warning(f"CLIP initialization failed (optional): {e}")
            self.clip_model = None
            self.clip_processor = None

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        if not self.text_encoder or not text:
            return []

        try:
            embedding = self.text_encoder.encode(text, convert_to_numpy=False)
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        except Exception as e:
            logger.error(f"Text embedding failed: {e}")
            return []

    def embed_texts_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently"""
        if not self.text_encoder or not texts:
            return []

        try:
            # Filter empty texts
            non_empty_texts = [t for t in texts if t and len(t.strip()) > 0]

            if not non_empty_texts:
                return []

            # Batch encode for efficiency
            embeddings = self.text_encoder.encode(
                non_empty_texts,
                batch_size=32,  # Process 32 texts at a time
                show_progress_bar=False,
                convert_to_numpy=False
            )

            # Convert to list format
            result = []
            for emb in embeddings:
                if hasattr(emb, 'tolist'):
                    result.append(emb.tolist())
                else:
                    result.append(list(emb))

            logger.debug(f"Generated {len(result)} embeddings for batch")
            return result

        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return []

    def embed_image(self, image_path: str) -> List[float]:
        """Generate embedding for image using CLIP"""
        if not self.clip_model or not self.clip_processor:
            logger.warning("CLIP not available for image embedding")
            return []

        try:
            from PIL import Image

            # Load and process image
            image = Image.open(image_path).convert("RGB")

            # Get CLIP embedding for image
            inputs = self.clip_processor(images=image, return_tensors="pt")
            image_features = self.clip_model.get_image_features(**inputs)

            # Normalize and convert to list
            embedding = image_features.detach().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Image embedding failed for {image_path}: {e}")
            return []

    def embed_table(self, table_text: str, table_metadata: dict = None) -> List[float]:
        """Generate embedding for table (treats as text)"""
        if not table_text:
            return []

        try:
            # Add table context to embedding
            enhanced_text = f"Table: {table_text}"

            return self.embed_text(enhanced_text)

        except Exception as e:
            logger.error(f"Table embedding failed: {e}")
            return []

    def embed_composite(self, text: str, image_path: str = None) -> List[float]:
        """
        Generate embedding for composite content.
        Combines text and image embeddings.
        """
        embeddings = []

        # Get text embedding
        if text:
            text_emb = self.embed_text(text)
            if text_emb:
                embeddings.append(np.array(text_emb))

        # Get image embedding
        if image_path:
            image_emb = self.embed_image(image_path)
            if image_emb:
                embeddings.append(np.array(image_emb))

        # Average embeddings if both available
        if embeddings:
            if len(embeddings) == 1:
                return embeddings[0].tolist()
            else:
                # Average multiple embeddings
                composite = np.mean(embeddings, axis=0)
                # Normalize
                composite = composite / np.linalg.norm(composite)
                return composite.tolist()

        return []

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        Returns value between -1 and 1 (typically 0 to 1 for normalized embeddings).
        """
        if not embedding1 or not embedding2:
            return 0.0

        try:
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)

            # Cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            return float(similarity)

        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    def get_embedding_dim(self) -> int:
        """Get embedding dimensionality"""
        return self.embedding_dim
