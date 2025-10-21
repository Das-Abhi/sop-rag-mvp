# Text extraction module
"""
Text extraction from PDF documents using pdfplumber and PaddleOCR
"""
from typing import List, Dict, Tuple
import pdfplumber
from paddleocr import PaddleOCR
import re
from loguru import logger

class TextExtractor:
    """
    Extracts text from PDF regions and images.
    KISS principle: Simple, focused extraction without complex preprocessing.
    """

    def __init__(self):
        # Initialize PaddleOCR for image text extraction
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            logger.info("PaddleOCR initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self.ocr = None

    def extract_from_region(self, pdf_path: str, bbox: Tuple[float, float, float, float]) -> str:
        """Extract text from a specific region (bbox) on a page"""
        text = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Crop page to region and extract text
                    cropped = page.crop(bbox)
                    text += cropped.extract_text() or ""

        except Exception as e:
            logger.error(f"Error extracting from region {bbox}: {e}")

        return self.clean_text(text)

    def extract_page(self, pdf_path: str, page_num: int) -> str:
        """Extract all text from a specific page"""
        text = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text() or ""

        except Exception as e:
            logger.error(f"Error extracting page {page_num}: {e}")

        return self.clean_text(text)

    def extract_with_ocr(self, image_path: str) -> str:
        """Extract text from image using PaddleOCR"""
        if not self.ocr:
            logger.warning("PaddleOCR not available")
            return ""

        try:
            # Run OCR on image
            result = self.ocr.ocr(image_path, cls=True)

            # Extract text from result
            text_lines = []
            for line in result:
                if line:
                    for item in line:
                        text, confidence = item[1]
                        if confidence > 0.3:  # Only include confident predictions
                            text_lines.append(text)

            return self.clean_text(" ".join(text_lines))

        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """
        Clean extracted text:
        - Remove extra whitespace
        - Normalize line breaks
        - Remove control characters
        """
        if not text:
            return ""

        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)

        # Normalize multiple newlines to single newline
        text = re.sub(r'\n\n+', '\n', text)

        # Normalize multiple spaces
        text = re.sub(r' {2,}', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text
