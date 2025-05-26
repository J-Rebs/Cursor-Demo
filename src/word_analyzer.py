import os
import logging
import re
from collections import Counter
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class WordAnalyzer:
    """Analyzes word frequencies and sentiment in risk sections using VADER."""
    
    def __init__(self):
        logger.info("Initializing WordAnalyzer with VADER...")
        # Initialize VADER
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Expanded list of common words to ignore
        self.stop_words = {
            # Articles
            'the', 'a', 'an',
            # Prepositions
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'from', 'about', 'like', 'through', 'over', 'before', 'between', 'after', 'since', 'without', 'under', 'within', 'along', 'following', 'across', 'behind', 'beyond', 'plus', 'except', 'but', 'up', 'out', 'around', 'down', 'off', 'above', 'near',
            # Conjunctions
            'and', 'or', 'but', 'nor', 'for', 'yet', 'so', 'because', 'although', 'since', 'unless', 'while', 'where', 'if', 'than', 'though', 'whether',
            # Pronouns
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs', 'this', 'that', 'these', 'those', 'who', 'whom', 'whose', 'which', 'what', 'where', 'when', 'why', 'how',
            # Common verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could',
            # Common adjectives
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            # Numbers and common words
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third', 'fourth', 'fifth',
            # Document-specific words
            'item', 'risk', 'factors', 'unresolved', 'staff', 'comments', 'section', 'part', 'page', 'table', 'figure', 'note', 'notes',
            # Additional common words
            'also', 'however', 'therefore', 'thus', 'furthermore', 'moreover', 'nevertheless', 'nonetheless', 'accordingly', 'consequently', 'hence', 'meanwhile', 'subsequently', 'thereby', 'whereby'
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text for word frequency analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _get_word_frequencies(self, text: str) -> dict:
        """Get word frequencies from text."""
        # Clean text and split into words
        cleaned_text = self._clean_text(text)
        words = [word for word in cleaned_text.split() if word not in self.stop_words and len(word) > 2]
        
        # Count word frequencies
        word_counts = Counter(words)
        total_words = sum(word_counts.values())
        
        # Calculate percentages
        word_freq = {word: (count / total_words) * 100 for word, count in word_counts.items()}
        
        return word_freq
    
    def _get_word_sentiment(self, word: str) -> dict:
        """Get sentiment scores for a single word using VADER."""
        scores = self.sentiment_analyzer.polarity_scores(word)
        return {
            'compound': scores['compound'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'positive': scores['pos']
        }
    
    def _generate_histogram(self, word_frequencies: dict, output_path: str, title: str = "Word Frequency Distribution") -> None:
        """Generate a histogram of word frequencies."""
        # Get top 20 words
        top_words = dict(sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Create the plot
        plt.figure(figsize=(15, 8))
        plt.bar(top_words.keys(), top_words.values())
        plt.xticks(rotation=45, ha='right')
        plt.title(title)
        plt.xlabel('Words')
        plt.ylabel('Frequency (%)')
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(output_path)
        plt.close()
    
    def _generate_negative_words_histogram(self, words: list, output_path: str, title: str = "Most Negative Words") -> None:
        """Generate a histogram of the most negative words."""
        # Create the plot
        plt.figure(figsize=(15, 8))
        
        # Get words and their scores
        words_text = [w['word'] for w in words]
        scores = [w['negative'] for w in words]  # Use negative score instead of compound
        
        # Create horizontal bar plot
        plt.barh(range(len(words)), scores)
        plt.yticks(range(len(words)), words_text, fontsize=8)
        plt.title(title)
        plt.xlabel('Negative Sentiment Score')
        
        # Add value labels on the bars
        for i, v in enumerate(scores):
            plt.text(v, i, f'{v:.3f}', va='center', fontsize=8)
        
        # Adjust layout to prevent label cutoff
        plt.subplots_adjust(left=0.3)
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
    
    def analyze_word_frequencies(self, input_dir: str, output_dir: str) -> None:
        """Analyze word frequencies in risk sections and save results to CSV."""
        try:
            logger.info(f"Starting word frequency and sentiment analysis from {input_dir}")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get all risk factor files
            risk_files = [f for f in os.listdir(input_dir) if f.startswith('risk_') and f.endswith('.txt')]
            logger.info(f"Found {len(risk_files)} risk factor files to analyze")
            
            # List to store all results
            all_results = []
            
            for risk_file in tqdm(risk_files, desc="Analyzing risk factors"):
                # Read the risk factors file
                input_path = os.path.join(input_dir, risk_file)
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Get word frequencies
                word_freq = self._get_word_frequencies(text)
                
                # Get sentiment scores for each word
                word_scores = []
                for word, freq in word_freq.items():
                    if len(word) > 2:  # Only analyze words longer than 2 characters
                        scores = self._get_word_sentiment(word)
                        word_scores.append({
                            'word': word,
                            'frequency': freq,
                            **scores  # Include all sentiment scores
                        })
                
                # Sort by negative score (highest first)
                word_scores.sort(key=lambda x: x['negative'], reverse=True)
                
                # Get top 30 most negative words
                top_negative = word_scores[:30]
                
                # Generate histogram for this file
                hist_path = os.path.join(output_dir, f"negative_words_{risk_file.replace('.txt', '_hist.png')}")
                self._generate_negative_words_histogram(
                    top_negative,
                    hist_path,
                    f"Most Negative Words - {risk_file}"
                )
                
                # Add to results
                all_results.extend(word_scores)
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(all_results)
            output_path = os.path.join(output_dir, 'word_frequencies_summary.csv')
            df.to_csv(output_path, index=False)
            logger.info(f"Saved overall word frequency summary to {output_path}")
            
            # Generate overall histogram
            overall_hist_path = os.path.join(output_dir, 'negative_words_summary_hist.png')
            self._generate_negative_words_histogram(
                sorted(all_results, key=lambda x: x['negative'], reverse=True)[:30],
                overall_hist_path,
                "Overall Most Negative Words"
            )
            
        except Exception as e:
            logger.error(f"Error in word frequency analysis: {str(e)}", exc_info=True) 