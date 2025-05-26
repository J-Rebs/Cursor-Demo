import argparse
import logging
from data_extractor import DataExtractor
import sys
from datetime import datetime
import os
from risk_extractor import RiskExtractor
from word_analyzer import WordAnalyzer
from sentence_analyzer import SentenceAnalyzer
from report_generator import ReportGenerator

def setup_logging():
    """Set up logging configuration."""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'risk_analysis_{timestamp}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger

def main():
    """Main function to run the risk analysis pipeline."""
    parser = argparse.ArgumentParser(description='Analyze risk factors from 10-K PDFs')
    parser.add_argument('--input', required=True, help='Input directory containing PDF files')
    parser.add_argument('--output', required=True, help='Output directory for analysis results')
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info("Starting risk analysis...")
    
    try:
        # Step 1: Extract text from PDFs
        logger.info("Step 1: Extracting text from PDFs")
        data_extractor = DataExtractor()
        extracted_texts_dir = os.path.join(args.output, 'extracted_texts')
        data_extractor.extract_data(args.input, extracted_texts_dir)
        
        # Step 2: Extract risk factors
        logger.info("Step 2: Extracting risk factors")
        risk_extractor = RiskExtractor()
        risk_factors_dir = os.path.join(args.output, 'risk_factors')
        risk_extractor.extract_risks(extracted_texts_dir, risk_factors_dir)
        
        # Step 3: Analyze word frequencies and sentiment
        logger.info("Step 3: Analyzing word frequencies and sentiment using VADER")
        word_analyzer = WordAnalyzer()
        analysis_dir = os.path.join(args.output, 'analysis')
        word_analyzer.analyze_word_frequencies(risk_factors_dir, analysis_dir)
        
        # Step 4: Analyze sentences using FinBERT
        logger.info("Step 4: Analyzing sentences using FinBERT")
        sentence_analyzer = SentenceAnalyzer()
        sentence_analyzer.analyze_sentences(risk_factors_dir, analysis_dir)
        
        # Step 5: Generate report
        logger.info("Step 5: Generating analysis report")
        report_generator = ReportGenerator()
        report_generator.generate_report(analysis_dir, args.output)
        
        logger.info("Analysis complete!")
        
    except Exception as e:
        logger.error(f"Error in main pipeline: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 