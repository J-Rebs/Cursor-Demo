import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re
from tqdm import tqdm
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

logger = logging.getLogger(__name__)

class DataExtractor:
    """Extracts text from 10-K PDFs."""
    
    def __init__(self):
        logger.info("Initializing DataExtractor...")
    
    def _clean_text(self, text: str) -> str:
        """Clean up extracted text for better readability."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Add newlines after sentences
        text = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\2', text)
        
        # Remove page numbers and headers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'Apple Inc\. \| \d{4} Form 10-K \| \d+\s*', '', text)
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file using pdfminer with improved layout analysis."""
        output_string = StringIO()
        try:
            with open(pdf_path, 'rb') as in_file:
                parser = PDFParser(in_file)
                doc = PDFDocument(parser)
                rsrcmgr = PDFResourceManager()
                
                # Configure layout parameters for better text extraction
                laparams = LAParams(
                    line_overlap=0.5,
                    char_margin=2.0,
                    line_margin=0.5,
                    word_margin=0.1,
                    boxes_flow=0.5,
                    detect_vertical=False,
                    all_texts=False
                )
                
                device = TextConverter(rsrcmgr, output_string, laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                
                for page in PDFPage.create_pages(doc):
                    interpreter.process_page(page)
                
                text = output_string.getvalue()
                return self._clean_text(text)
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
            return ""
        finally:
            output_string.close()
    
    def _extract_year_from_filename(self, filename: str) -> int:
        """Extract year from filename or use current year if not found."""
        try:
            # Try to find year in filename
            year_match = re.search(r'20\d{2}', filename)
            if year_match:
                return int(year_match.group())
        except:
            pass
        
        # Default to current year if no year found
        return datetime.now().year
    
    def extract_data(self, pdf_dir: str, output_dir: str = 'data') -> None:
        """Extract text from PDFs and save each to a separate text file."""
        try:
            logger.info(f"Starting text extraction from PDFs in {pdf_dir}")
            
            # Create output directory if it doesn't exist
            text_output_dir = os.path.join(output_dir, 'extracted_texts')
            os.makedirs(text_output_dir, exist_ok=True)
            
            # Process PDFs
            pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
            logger.info(f"Found {len(pdf_files)} PDF files to analyze")
            
            for pdf_file in tqdm(pdf_files, desc="Analyzing PDFs"):
                pdf_path = os.path.join(pdf_dir, pdf_file)
                logger.info(f"Processing {pdf_file}")
                
                # Extract text from PDF
                text = self._extract_text_from_pdf(pdf_path)
                if not text:
                    logger.warning(f"Could not extract text from {pdf_file}")
                    continue
                
                # Extract year from filename
                year = self._extract_year_from_filename(pdf_file)
                
                # Create output filename
                base_name = os.path.splitext(pdf_file)[0]
                output_file = os.path.join(text_output_dir, f"{base_name}_{year}.txt")
                
                # Save text to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                logger.info(f"Saved extracted text to {output_file}")
            
            logger.info(f"Extraction complete. Results saved to {text_output_dir}")
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}", exc_info=True) 