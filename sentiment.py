"""
Sentiment Analysis Module for TikTok comments
Uses lexicon-based approach with Indonesian sentiment dictionary
"""

import json
import os
from typing import List, Dict, Tuple
from utils import clean_text, tokenize

# Path to lexicon file
LEXICON_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'lexicon_id.json')

# Global lexicon cache
_lexicon = None


def load_lexicon() -> Dict:
    """Load sentiment lexicon from JSON file"""
    global _lexicon
    
    if _lexicon is not None:
        return _lexicon
    
    try:
        with open(LEXICON_PATH, 'r', encoding='utf-8') as f:
            _lexicon = json.load(f)
        return _lexicon
    except FileNotFoundError:
        print(f"Warning: Lexicon file not found at {LEXICON_PATH}")
        _lexicon = {"positif": {}, "negatif": {}, "intensifier": {}, "negator": {}}
        return _lexicon


def calculate_sentiment_score(text: str) -> float:
    """
    Calculate sentiment score for a single text
    
    Returns:
        Float score: positive values = positive sentiment
                    negative values = negative sentiment
                    around 0 = neutral
    """
    lexicon = load_lexicon()
    
    # Clean and tokenize
    cleaned = clean_text(text, normalize=True)
    words = tokenize(cleaned)
    
    if not words:
        return 0.0
    
    score = 0.0
    prev_word = ""
    prev_prev_word = ""
    
    for i, word in enumerate(words):
        word_score = 0.0
        
        # Check positive words
        if word in lexicon.get('positif', {}):
            word_score = lexicon['positif'][word]
        
        # Check negative words
        elif word in lexicon.get('negatif', {}):
            word_score = lexicon['negatif'][word]
        
        # Apply negator (reverses sentiment)
        if prev_word in lexicon.get('negator', {}):
            negator_value = lexicon['negator'][prev_word]
            word_score = word_score * negator_value
        
        # Apply intensifier (amplifies sentiment)
        if prev_word in lexicon.get('intensifier', {}):
            intensifier_value = lexicon['intensifier'][prev_word]
            word_score = word_score * intensifier_value
        
        # Check two words back for intensifier
        if prev_prev_word in lexicon.get('intensifier', {}):
            intensifier_value = lexicon['intensifier'][prev_prev_word]
            word_score = word_score * (intensifier_value * 0.5)  # Reduced effect
        
        score += word_score
        prev_prev_word = prev_word
        prev_word = word
    
    # Normalize by text length (with minimum)
    normalized_score = score / max(len(words), 1)
    
    return round(normalized_score, 3)


def classify_sentiment(score: float, 
                       positive_threshold: float = 0.1,
                       negative_threshold: float = -0.1) -> str:
    """
    Classify sentiment based on score
    
    Args:
        score: Sentiment score
        positive_threshold: Score above this = positive
        negative_threshold: Score below this = negative
    
    Returns:
        'positive', 'negative', or 'neutral'
    """
    if score > positive_threshold:
        return 'positive'
    elif score < negative_threshold:
        return 'negative'
    else:
        return 'neutral'


def analyze_text(text: str) -> Dict:
    """
    Analyze sentiment of a single text
    
    Returns:
        Dict with score, label, and cleaned text
    """
    cleaned = clean_text(text, normalize=True)
    score = calculate_sentiment_score(text)
    label = classify_sentiment(score)
    
    return {
        'original_text': text,
        'cleaned_text': cleaned,
        'sentiment_score': score,
        'sentiment_label': label
    }


def analyze_batch(texts: List[str]) -> List[Dict]:
    """
    Analyze sentiment for a batch of texts
    
    Args:
        texts: List of text strings
    
    Returns:
        List of analysis results
    """
    results = []
    for text in texts:
        result = analyze_text(text)
        results.append(result)
    return results


def get_sentiment_summary(results: List[Dict]) -> Dict:
    """
    Get summary statistics from analysis results
    
    Returns:
        Dict with counts, percentages, and average score
    """
    if not results:
        return {
            'total': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'positive_pct': 0,
            'negative_pct': 0,
            'neutral_pct': 0,
            'avg_score': 0
        }
    
    total = len(results)
    positive = sum(1 for r in results if r['sentiment_label'] == 'positive')
    negative = sum(1 for r in results if r['sentiment_label'] == 'negative')
    neutral = sum(1 for r in results if r['sentiment_label'] == 'neutral')
    avg_score = sum(r['sentiment_score'] for r in results) / total
    
    return {
        'total': total,
        'positive_count': positive,
        'negative_count': negative,
        'neutral_count': neutral,
        'positive_pct': round(positive / total * 100, 1),
        'negative_pct': round(negative / total * 100, 1),
        'neutral_pct': round(neutral / total * 100, 1),
        'avg_score': round(avg_score, 3)
    }


def get_top_words(results: List[Dict], sentiment: str = None, top_n: int = 20) -> Dict[str, int]:
    """
    Get most frequent words, optionally filtered by sentiment
    
    Args:
        results: Analysis results
        sentiment: Filter by 'positive', 'negative', or None for all
        top_n: Number of top words to return
    
    Returns:
        Dict of word: count
    """
    word_freq = {}
    
    for result in results:
        if sentiment and result['sentiment_label'] != sentiment:
            continue
        
        words = tokenize(result['cleaned_text'])
        for word in words:
            if len(word) > 2:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_words[:top_n])


# Quick test
if __name__ == "__main__":
    test_comments = [
        "Bagus banget produknya, recommended!",
        "Jelek parah, nyesel beli",
        "Biasa aja sih menurutku",
        "Worth it banget! Gak nyesel",
        "Zonk, gak sesuai ekspektasi"
    ]
    
    results = analyze_batch(test_comments)
    for r in results:
        print(f"{r['sentiment_label']:>10} ({r['sentiment_score']:>6.3f}): {r['original_text']}")
    
    print("\n--- Summary ---")
    summary = get_sentiment_summary(results)
    print(f"Positive: {summary['positive_count']} ({summary['positive_pct']}%)")
    print(f"Negative: {summary['negative_count']} ({summary['negative_pct']}%)")
    print(f"Neutral:  {summary['neutral_count']} ({summary['neutral_pct']}%)")
