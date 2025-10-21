# Layout analysis module
"""
PDF layout analysis for identifying regions:
- Text blocks
- Images (diagrams, flowcharts)
- Tables (simple and complex)
- Composite content
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
import pdfplumber
import pymupdf as fitz
from loguru import logger

@dataclass
class Region:
    """Represents a region in a PDF page"""
    type: str  # 'text', 'image', 'table', 'composite'
    bbox: Tuple[float, float, float, float]
    page_number: int
    confidence: float
    metadata: Dict

class LayoutAnalyzer:
    """
    Analyzes PDF layout to identify distinct regions using pdfplumber and pymupdf.
    KISS principle: Focus on reliable detection, minimal complexity.
    """

    def __init__(self):
        self.text_size_threshold = 10
        self.image_min_area = 5000  # pixels
        self.table_min_rows = 2
        logger.debug("LayoutAnalyzer initialized")

    def analyze_page(self, pdf_path: str, page_num: int) -> List[Region]:
        """Analyze single page and detect all regions in reading order"""
        regions = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_num]

                # Detect tables first (most structured content)
                table_regions = self._detect_tables(page, page_num)
                regions.extend(table_regions)
                logger.debug(f"Found {len(table_regions)} tables on page {page_num}")

                # Detect images
                image_regions = self._detect_images(pdf_path, page_num)
                regions.extend(image_regions)
                logger.debug(f"Found {len(image_regions)} images on page {page_num}")

                # Detect text blocks (excluding table/image areas)
                text_regions = self._detect_text_blocks(page, page_num, regions)
                regions.extend(text_regions)
                logger.debug(f"Found {len(text_regions)} text blocks on page {page_num}")

        except Exception as e:
            logger.error(f"Error analyzing page {page_num}: {e}")
            return []

        return self._sort_regions_by_reading_order(regions)

    def _detect_tables(self, page, page_num: int) -> List[Region]:
        """Detect table regions using pdfplumber's table detection"""
        tables = []

        try:
            # Use strict line detection for reliable table boundaries
            table_settings = {
                "vertical_strategy": "lines_strict",
                "horizontal_strategy": "lines_strict",
                "intersection_tolerance": 3,
            }

            detected_tables = page.find_tables(table_settings=table_settings)

            for idx, table in enumerate(detected_tables):
                if len(table.rows) >= self.table_min_rows:
                    tables.append(Region(
                        type='table',
                        bbox=table.bbox,
                        page_number=page_num,
                        confidence=0.95,  # High confidence for strict line detection
                        metadata={
                            'table_id': idx,
                            'rows': len(table.rows),
                            'cols': len(table.rows[0]) if table.rows else 0
                        }
                    ))
        except Exception as e:
            logger.warning(f"Table detection failed on page {page_num}: {e}")

        return tables

    def _detect_images(self, pdf_path: str, page_num: int) -> List[Region]:
        """Detect image regions using pymupdf"""
        images = []

        try:
            doc = fitz.open(pdf_path)
            page = doc[page_num]

            # Get list of images on the page
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)

                # Calculate image area
                image_area = pix.width * pix.height

                if image_area >= self.image_min_area:
                    # Get image bounding box
                    img_rect = page.get_image_rects(xref)[0] if page.get_image_rects(xref) else None

                    if img_rect:
                        images.append(Region(
                            type='image',
                            bbox=img_rect.to_rect().to_quad().get_rect(),
                            page_number=page_num,
                            confidence=0.9,
                            metadata={
                                'image_id': img_index,
                                'width': pix.width,
                                'height': pix.height,
                                'xref': xref
                            }
                        ))

            doc.close()
        except Exception as e:
            logger.warning(f"Image detection failed on page {page_num}: {e}")

        return images

    def _detect_text_blocks(self, page, page_num: int, regions: List[Region]) -> List[Region]:
        """Detect text blocks, excluding table and image areas"""
        text_regions = []

        try:
            # Get all text from page
            blocks = page.extract_blocks()

            # Create bboxes for tables and images for exclusion
            excluded_bboxes = [r.bbox for r in regions if r.type in ['table', 'image']]

            for block in blocks:
                if isinstance(block, dict) and 'rect' in block:
                    bbox = block['rect']
                    text = block.get('text', '').strip()

                    # Skip empty blocks
                    if not text or len(text) < 3:
                        continue

                    # Check if block overlaps with excluded regions
                    if self._overlaps_with_any(bbox, excluded_bboxes):
                        continue

                    text_regions.append(Region(
                        type='text',
                        bbox=bbox,
                        page_number=page_num,
                        confidence=0.85,
                        metadata={
                            'text_preview': text[:50],
                            'text_length': len(text)
                        }
                    ))
        except Exception as e:
            logger.warning(f"Text block detection failed on page {page_num}: {e}")

        return text_regions

    def _overlaps_with_any(self, bbox: Tuple, excluded_bboxes: List[Tuple]) -> bool:
        """Check if bbox overlaps with any excluded bbox"""
        x0, top, x1, bottom = bbox

        for ex0, ex_top, ex1, ex_bottom in excluded_bboxes:
            # Check for overlap
            if not (x1 < ex0 or x0 > ex1 or bottom < ex_top or top > ex_bottom):
                return True

        return False

    def _sort_regions_by_reading_order(self, regions: List[Region]) -> List[Region]:
        """Sort regions by reading order (top-left to bottom-right)"""
        return sorted(regions, key=lambda r: (r.bbox[1], r.bbox[0]))
