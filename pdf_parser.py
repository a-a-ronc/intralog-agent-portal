"""
PDF parsing utilities for extracting title block metadata.
"""

import re
import os
from typing import Dict, Optional, List
import pdfplumber
from logger_config import setup_logger

class PDFParser:
    """Extracts metadata from PDF title blocks."""
    
    def __init__(self):
        self.logger = setup_logger()
        
        # Common patterns for title block fields
        self.patterns = {
            'customer': [
                r'customer[:\s]+(.*?)(?:\n|$)',
                r'client[:\s]+(.*?)(?:\n|$)',
                r'company[:\s]+(.*?)(?:\n|$)',
                r'job\s+for[:\s]+(.*?)(?:\n|$)'
            ],
            'address': [
                r'address[:\s]+(.*?)(?:\n|$)',
                r'location[:\s]+(.*?)(?:\n|$)',
                r'site[:\s]+(.*?)(?:\n|$)',
                r'facility[:\s]+(.*?)(?:\n|$)'
            ],
            'project_manager': [
                r'project\s+manager[:\s]+(.*?)(?:\n|$)',
                r'pm[:\s]+(.*?)(?:\n|$)',
                r'manager[:\s]+(.*?)(?:\n|$)',
                r'salesperson[:\s]+(.*?)(?:\n|$)'
            ],
            'drafter': [
                r'drawn\s+by[:\s]+(.*?)(?:\n|$)',
                r'drafter[:\s]+(.*?)(?:\n|$)',
                r'designer[:\s]+(.*?)(?:\n|$)',
                r'drafted[:\s]+(.*?)(?:\n|$)'
            ],
            'project_name': [
                r'project\s+name[:\s]+(.*?)(?:\n|$)',
                r'job\s+name[:\s]+(.*?)(?:\n|$)',
                r'title[:\s]+(.*?)(?:\n|$)',
                r'description[:\s]+(.*?)(?:\n|$)'
            ]
        }
    
    def extract_title_block(self, pdf_path: str) -> Optional[Dict[str, str]]:
        """Extract title block information from PDF."""
        try:
            if not os.path.exists(pdf_path):
                self.logger.error(f"PDF file not found: {pdf_path}")
                return None
            
            self.logger.info(f"Extracting metadata from PDF: {pdf_path}")
            
            with pdfplumber.open(pdf_path) as pdf:
                # Usually title block is on the first page
                if not pdf.pages:
                    self.logger.error("PDF has no pages")
                    return None
                
                # Extract text from first page
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                if not text:
                    self.logger.error("No text found in PDF")
                    return None
                
                # Clean up text
                text = text.lower()
                text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                
                # Extract metadata using patterns
                metadata = self._extract_fields(text)
                
                # Validate required fields
                if not self._validate_metadata(metadata):
                    self.logger.warning("Incomplete metadata extracted from PDF")
                
                self.logger.info(f"Extracted metadata: {metadata}")
                return metadata
        
        except Exception as e:
            self.logger.error(f"Error extracting PDF metadata: {str(e)}")
            return None
    
    def _extract_fields(self, text: str) -> Dict[str, str]:
        """Extract specific fields from text using regex patterns."""
        metadata = {}
        
        for field_name, patterns in self.patterns.items():
            value = self._extract_field_value(text, patterns)
            if value:
                metadata[field_name] = self._clean_field_value(value)
        
        return metadata
    
    def _extract_field_value(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract field value using multiple regex patterns."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if value and len(value) > 1:  # Ignore single characters
                    return value
        return None
    
    def _clean_field_value(self, value: str) -> str:
        """Clean and normalize field values."""
        # Remove extra whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Remove common artifacts
        value = re.sub(r'[_\-]{3,}', '', value)  # Remove long dashes/underscores
        value = re.sub(r'[\r\n\t]', ' ', value)  # Remove line breaks and tabs
        
        # Capitalize properly
        if value:
            # Don't capitalize if it looks like an email
            if '@' not in value:
                value = value.title()
        
        return value
    
    def _validate_metadata(self, metadata: Dict[str, str]) -> bool:
        """Validate that we have the minimum required metadata."""
        required_fields = ['customer', 'project_manager']
        
        for field in required_fields:
            if field not in metadata or not metadata[field].strip():
                return False
        
        return True
    
    def extract_text_regions(self, pdf_path: str) -> List[Dict[str, any]]:
        """Extract text with position information for more precise parsing."""
        try:
            regions = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract words with positions
                    words = page.extract_words()
                    
                    for word in words:
                        regions.append({
                            'text': word['text'],
                            'x0': word['x0'],
                            'y0': word['y0'], 
                            'x1': word['x1'],
                            'y1': word['y1'],
                            'page': page_num
                        })
            
            return regions
            
        except Exception as e:
            self.logger.error(f"Error extracting text regions: {str(e)}")
            return []
    
    def find_title_block_region(self, pdf_path: str) -> Optional[Dict[str, any]]:
        """Attempt to locate the title block region in the PDF."""
        try:
            regions = self.extract_text_regions(pdf_path)
            
            # Title blocks are typically in bottom-right corner
            # Look for common title block keywords
            title_block_keywords = [
                'drawn by', 'project manager', 'customer', 'date', 'scale',
                'sheet', 'revision', 'checked', 'approved'
            ]
            
            keyword_regions = []
            for region in regions:
                text = region['text'].lower()
                for keyword in title_block_keywords:
                    if keyword in text:
                        keyword_regions.append(region)
                        break
            
            if keyword_regions:
                # Find bounding box of title block area
                min_x = min(r['x0'] for r in keyword_regions)
                min_y = min(r['y0'] for r in keyword_regions)
                max_x = max(r['x1'] for r in keyword_regions)
                max_y = max(r['y1'] for r in keyword_regions)
                
                return {
                    'x0': min_x, 'y0': min_y,
                    'x1': max_x, 'y1': max_y,
                    'regions': keyword_regions
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding title block region: {str(e)}")
            return None
