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
            
            # Add word frequency analysis section if available
            word_freq_path = os.path.join(analysis_dir, 'word_frequencies_summary.csv')
            word_freq_vis_path = os.path.join(analysis_dir, 'word_frequencies_summary_hist.png')
            if os.path.exists(word_freq_path) and os.path.exists(word_freq_vis_path):
                report.append("## Most Frequent Words")
                report.append("\nThe following visualization shows the most frequently occurring words in the risk factors, regardless of their sentiment:\n")
                report.append("![Word Frequency Analysis](analysis/word_frequencies_summary_hist.png)\n")
            
            # Add negative words section if available
            neg_words_vis_path = os.path.join(analysis_dir, 'negative_words_summary_hist.png')
            if os.path.exists(neg_words_vis_path):
                report.append("## Most Negative Words")
                report.append("\nThe following visualization shows the words with the most negative sentiment scores:\n")
                report.append("![Negative Words Analysis](analysis/negative_words_summary_hist.png)\n")
                
                # Add top negative words from the CSV
                try:
                    word_freq_df = pd.read_csv(word_freq_path)
                    # Sort by negative sentiment score and get top 10
                    negative_words = word_freq_df.sort_values('negative', ascending=False).head(10)
                    report.append("\n### Top 10 Most Negative Words\n")
                    for _, row in negative_words.iterrows():
                        report.append(f"- **{row['word']}** (Negative Score: {row['negative']:.3f})\n")
                except Exception as e:
                    logger.error(f"Error processing word frequency data: {str(e)}")
            
            # Add negative sentences section if available
            sentence_sentiment_path = os.path.join(analysis_dir, 'sentence_sentiment_summary.csv')
            if os.path.exists(sentence_sentiment_path):
                try:
                    sentence_sentiment_df = pd.read_csv(sentence_sentiment_path)
                    # Filter for negative sentences and sort by score
                    negative_sentences = sentence_sentiment_df[sentence_sentiment_df['label'] == 'negative'].sort_values('score', ascending=False).head(5)
                    
                    if not negative_sentences.empty:
                        report.append("## Most Negative Sentences")
                        report.append("\nThe following sentences were identified as having the most negative sentiment using FinBERT:\n")
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