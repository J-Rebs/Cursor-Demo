import os
import logging
import re
import torch
import pandas as pd
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import nltk
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)

class SentenceAnalyzer:
    """Analyzes sentences in risk sections using FinBERT."""
    
    def __init__(self):
        logger.info("Initializing SentenceAnalyzer with FinBERT...")
        try:
            # Download NLTK sentence tokenizer
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            
            # Initialize FinBERT
            logger.info("Loading FinBERT model and tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert", cache_dir="models")
            self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert", cache_dir="models")
            
            # Move model to CPU if CUDA is not available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            # Map sentiment labels
            self.label_map = {0: "positive", 1: "negative", 2: "neutral"}
            logger.info("FinBERT model and tokenizer loaded successfully")
            
        except Exception as e:
            logger.error(f"Error initializing FinBERT: {str(e)}")
            raise
    
    def _clean_sentence(self, sentence: str) -> str:
        """Clean and normalize a sentence for analysis."""
        # Remove extra whitespace
        sentence = re.sub(r'\s+', ' ', sentence.strip())
        # Remove common document artifacts
        sentence = re.sub(r'^\d+\.\s*', '', sentence)  # Remove leading numbers
        sentence = re.sub(r'^[A-Z]\.\s*', '', sentence)  # Remove leading letters
        return sentence
    
    def _get_sentence_sentiment(self, sentence: str) -> dict:
        """Get sentiment score for a single sentence using FinBERT."""
        try:
            # Clean and prepare sentence
            sentence = self._clean_sentence(sentence)
            if not sentence or len(sentence.split()) <= 3:
                return None
            
            # Tokenize and prepare input
            inputs = self.tokenizer(sentence, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1)[0]
                
            # Get the highest probability label and score
            label_idx = torch.argmax(scores).item()
            score = scores[label_idx].item()
            
            return {
                'label': self.label_map[label_idx],
                'score': score,
                'sentence': sentence
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentence: {str(e)}")
            return None
    
    def analyze_sentences(self, input_dir: str, output_dir: str) -> None:
        """Analyze sentences in risk sections and save results to CSV."""
        try:
            logger.info(f"Starting sentence analysis from {input_dir}")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get all risk factor files
            risk_files = [f for f in os.listdir(input_dir) if f.startswith('risk_') and f.endswith('.txt')]
            logger.info(f"Found {len(risk_files)} risk factor files to analyze")
            
            # Dictionary to store unique sentences and their analysis
            unique_sentences = {}
            
            for risk_file in tqdm(risk_files, desc="Analyzing sentences"):
                try:
                    # Read the risk factors file
                    input_path = os.path.join(input_dir, risk_file)
                    with open(input_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    # Split into sentences and clean
                    sentences = [self._clean_sentence(s) for s in sent_tokenize(text)]
                    sentences = [s for s in sentences if s and len(s.split()) > 3]  # Filter out short sentences
                    
                    # Get sentiment scores for each sentence
                    for sentence in sentences:
                        if sentence not in unique_sentences:
                            score = self._get_sentence_sentiment(sentence)
                            if score:
                                score['file'] = risk_file
                                unique_sentences[sentence] = score
                        
                except Exception as e:
                    logger.error(f"Error processing file {risk_file}: {str(e)}")
                    continue
            
            if unique_sentences:
                # Convert to list and sort by negative score
                all_results = list(unique_sentences.values())
                all_results.sort(key=lambda x: x['score'] if x['label'] == 'negative' else 0, reverse=True)
                
                # Create DataFrame and save to CSV
                df = pd.DataFrame(all_results)
                output_path = os.path.join(output_dir, 'sentence_sentiment_summary.csv')
                df.to_csv(output_path, index=False)
                logger.info(f"Saved overall sentence sentiment summary to {output_path}")
                
                # Save individual file results
                for risk_file in risk_files:
                    file_results = [r for r in all_results if r['file'] == risk_file]
                    if file_results:
                        df = pd.DataFrame(file_results)
                        output_path = os.path.join(output_dir, f"sentence_sentiment_{risk_file.replace('.txt', '.csv')}")
                        df.to_csv(output_path, index=False)
                        logger.info(f"Saved sentence sentiment analysis for {risk_file} to {output_path}")
            else:
                logger.warning("No results were generated from the analysis")
            
        except Exception as e:
            logger.error(f"Error in sentence analysis: {str(e)}", exc_info=True) 