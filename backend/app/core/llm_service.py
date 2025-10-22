# LLM service
"""
Language model integration with Ollama
"""
from typing import Optional, List, Dict
import requests
from loguru import logger
import os


class LLMService:
    """Ollama-based language model service"""

    def __init__(
        self,
        primary_model: str = "llama3.1:8b",
        fallback_model: str = "mistral:7b",
        ollama_host: Optional[str] = None
    ):
        """
        Initialize LLM Service

        Args:
            primary_model: Primary LLM model name
            fallback_model: Fallback model if primary fails
            ollama_host: Ollama API endpoint
        """
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.temperature = 0.3
        self.max_tokens = 1024

        # Test connection
        if not self.check_model_health():
            logger.warning(f"Could not connect to Ollama at {self.ollama_host}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Generate text using LLM

        Args:
            prompt: Input prompt
            system_prompt: System instruction (not used in basic generation)
            temperature: Sampling temperature
            model: Model to use (default: primary)

        Returns:
            Generated text
        """
        model = model or self.primary_model
        temperature = temperature or self.temperature

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "num_predict": self.max_tokens,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            generated_text = result.get("response", "").strip()
            logger.debug(f"Generated text from {model} ({len(generated_text)} chars)")
            return generated_text

        except Exception as e:
            logger.error(f"Error generating with {model}: {e}")
            # Try fallback model
            if model != self.fallback_model:
                logger.info(f"Trying fallback model: {self.fallback_model}")
                return self.generate(prompt, system_prompt, temperature, self.fallback_model)
            return ""

    def generate_with_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Generate response with context

        Args:
            query: User query
            context: Retrieved context
            system_prompt: System instruction
            model: Model to use

        Returns:
            Generated response
        """
        if system_prompt is None:
            system_prompt = "You are a helpful assistant. Answer the question based on the provided context."

        # Build full prompt
        full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        return self.generate(full_prompt, model=model)

    def extract_citations(self, response: str, context_chunks: List[Dict]) -> Dict:
        """
        Extract and map citations in response

        Args:
            response: Generated response
            context_chunks: Source chunks used

        Returns:
            Dictionary with response and mapped citations
        """
        try:
            citations = []
            for i, chunk in enumerate(context_chunks):
                source = chunk.get("metadata", {}).get("source_file", f"Source {i+1}")
                page = chunk.get("metadata", {}).get("page_num")

                citation = {
                    "index": i + 1,
                    "source": source,
                    "page": page,
                    "content_preview": chunk.get("content", "")[:150]
                }
                citations.append(citation)

            logger.debug(f"Extracted {len(citations)} citations")
            return {
                "response": response,
                "citations": citations,
                "num_sources": len(context_chunks)
            }
        except Exception as e:
            logger.error(f"Error extracting citations: {e}")
            return {
                "response": response,
                "citations": [],
                "num_sources": 0
            }

    def summarize(self, text: str, max_length: int = 256) -> str:
        """
        Summarize text

        Args:
            text: Text to summarize
            max_length: Maximum summary length

        Returns:
            Summarized text
        """
        try:
            prompt = f"Summarize the following text in {max_length} characters or less:\n\n{text}\n\nSummary:"

            # Use lower temperature for more focused summaries
            return self.generate(prompt, temperature=0.1)

        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            # Fallback: return first max_length characters
            return text[:max_length]

    def check_model_health(self) -> bool:
        """
        Check if models are available

        Returns:
            True if at least primary model is available
        """
        try:
            response = requests.get(
                f"{self.ollama_host}/api/tags",
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]

            primary_available = any(self.primary_model in m for m in models)
            fallback_available = any(self.fallback_model in m for m in models)

            if primary_available:
                logger.info(f"LLM Service health check: OK (models available: {len(models)})")
                return True
            elif fallback_available:
                logger.warning(f"Primary model not available, fallback ready")
                return True
            else:
                logger.warning(f"No LLM models available. Available: {models}")
                return False

        except Exception as e:
            logger.error(f"LLM Service health check failed: {e}")
            return False

    def list_available_models(self) -> List[str]:
        """
        List all available models in Ollama

        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f"{self.ollama_host}/api/tags",
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            logger.info(f"Available models: {models}")
            return models

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
