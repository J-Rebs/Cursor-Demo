import os
import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates a markdown report summarizing the analysis results."""
    
    def __init__(self):
        logger.info("Initializing ReportGenerator...")
    
    def _clean_filename(self, filename: str) -> str:
        """Remove .txt and _2025 suffix from filenames."""
        return filename.replace('_2025.txt', '').replace('.txt', '')
    
    def generate_report(self, analysis_dir: str, output_dir: str) -> None:
        """Generate a markdown report summarizing the analysis results."""
        try:
            logger.info("Generating analysis report...")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate the markdown report
            report = []
            report.append("# Risk Analysis Report")
            report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            report.append("## Overview")
            report.append("\nThis report analyzes risk factors from financial documents using three different approaches:")
            report.append("1. Word frequency analysis to identify commonly used terms")
            report.append("2. Sentiment analysis of individual words using VADER")
            report.append("3. Sentence-level sentiment analysis using FinBERT\n")
            
            # Add word frequency analysis section if available
            word_freq_path = os.path.join(analysis_dir, 'word_frequencies_summary.csv')
            word_freq_vis_path = os.path.join(analysis_dir, 'word_frequencies_summary_hist.png')
            if os.path.exists(word_freq_path) and os.path.exists(word_freq_vis_path):
                report.append("## Word Frequency Analysis")
                report.append("\nThe following visualization shows the 20 most frequently occurring words in the risk factors, regardless of their sentiment. This helps identify key themes and topics in the risk sections.\n")
                report.append("![Most Frequent Words](analysis/word_frequencies_summary_hist.png)\n")
            
            # Add negative words section if available
            neg_words_vis_path = os.path.join(analysis_dir, 'negative_words_summary_hist.png')
            top_negative_path = os.path.join(analysis_dir, 'top_negative_words.csv')
            if os.path.exists(neg_words_vis_path) and os.path.exists(top_negative_path):
                report.append("## Negative Word Analysis")
                report.append("\nThis section shows words with the strongest negative sentiment scores, as determined by VADER sentiment analysis. The scores range from 0 (neutral) to 1 (extremely negative).\n")
                report.append("![Most Negative Words](analysis/negative_words_summary_hist.png)\n")
                
                # Add top negative words from the dedicated CSV
                try:
                    negative_words = pd.read_csv(top_negative_path)
                    report.append("\n### Top 10 Most Negative Words\n")
                    for _, row in negative_words.iterrows():
                        report.append(f"- **{row['word']}** (Negative Score: {row['negative']:.3f})\n")
                except Exception as e:
                    logger.error(f"Error processing negative words data: {str(e)}")
            
            # Add negative sentences section if available
            sentence_sentiment_path = os.path.join(analysis_dir, 'sentence_sentiment_summary.csv')
            if os.path.exists(sentence_sentiment_path):
                try:
                    sentence_sentiment_df = pd.read_csv(sentence_sentiment_path)
                    # Filter for negative sentences and sort by score
                    negative_sentences = sentence_sentiment_df[
                        (sentence_sentiment_df['label'] == 'negative') & 
                        (sentence_sentiment_df['score'] > 0.5)  # Only include high-confidence negative sentences
                    ].sort_values('score', ascending=False).head(5)
                    
                    if not negative_sentences.empty:
                        report.append("## Negative Sentence Analysis")
                        report.append("\nThe following sentences were identified as having the most negative sentiment using FinBERT, a specialized financial sentiment analysis model. The scores represent the model's confidence in the negative sentiment.\n")
                        for i, (_, row) in enumerate(negative_sentences.iterrows(), 1):
                            clean_filename = self._clean_filename(row['file'])
                            report.append(f"{i}. **Score: {row['score']:.3f}** - {row['sentence']} (from {clean_filename})\n")
                except Exception as e:
                    logger.error(f"Error processing sentence sentiment data: {str(e)}")
            
            # Write the report to file
            output_path = os.path.join(output_dir, 'output.md')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            logger.info(f"Report generated successfully at {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True) 