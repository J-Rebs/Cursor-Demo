import os
import logging
import re
from tqdm import tqdm

logger = logging.getLogger(__name__)

class RiskExtractor:
    """Extracts risk factors sections from extracted text files."""
    
    def __init__(self):
        logger.info("Initializing RiskExtractor...")
    
    def _extract_risk_section(self, text: str) -> str:
        """Extract text between Item 1A and Item 1B."""
        # Pattern to match text between Item 1A and Item 1B
        pattern = r'Item\s+1A\.?\s*Risk\s+Factors(.*?)(?=Item\s+1B\.?\s*Unresolved)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            risk_section = match.group(1).strip()
            # Clean up the text
            risk_section = re.sub(r'\n\s*\n', '\n\n', risk_section)  # Remove extra newlines
            risk_section = re.sub(r'\s+', ' ', risk_section)  # Remove extra spaces
            return risk_section
        return ""
    
    def extract_risks(self, input_dir: str, output_dir: str) -> None:
        """Extract risk factors from text files and save to a new directory."""
        try:
            logger.info(f"Starting risk factors extraction from {input_dir}")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get all text files
            text_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
            logger.info(f"Found {len(text_files)} text files to process")
            
            for text_file in tqdm(text_files, desc="Processing text files"):
                input_path = os.path.join(input_dir, text_file)
                output_path = os.path.join(output_dir, f"risk_{text_file}")
                
                # Read the text file
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Extract risk section
                risk_section = self._extract_risk_section(text)
                
                if risk_section:
                    # Save to new file
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(risk_section)
                    logger.info(f"Saved risk factors to {output_path}")
                else:
                    logger.warning(f"No risk factors found in {text_file}")
            
            logger.info(f"Extraction complete. Results saved to {output_dir}")
            
        except Exception as e:
            logger.error(f"Error in risk factors extraction: {str(e)}", exc_info=True) 