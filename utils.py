"""
Text preprocessing utilities for TikTok comments
Handles cleaning, normalization, and text preparation
"""

import re
import json
import os
from typing import List

# Common Indonesian slang normalization
SLANG_DICT = {
    'gak': 'tidak',
    'ga': 'tidak',
    'nggak': 'tidak',
    'enggak': 'tidak',
    'gk': 'tidak',
    'g': 'tidak',
    'tdk': 'tidak',
    'yg': 'yang',
    'dgn': 'dengan',
    'dg': 'dengan',
    'utk': 'untuk',
    'u/': 'untuk',
    'krn': 'karena',
    'krna': 'karena',
    'karna': 'karena',
    'tp': 'tapi',
    'tpi': 'tapi',
    'sm': 'sama',
    'sma': 'sama',
    'jg': 'juga',
    'jga': 'juga',
    'bgt': 'banget',
    'bngt': 'banget',
    'bngtt': 'banget',
    'bgtt': 'banget',
    'bet': 'banget',
    'skrg': 'sekarang',
    'skr': 'sekarang',
    'skg': 'sekarang',
    'bsk': 'besok',
    'kmrn': 'kemarin',
    'kmrin': 'kemarin',
    'blm': 'belum',
    'blom': 'belum',
    'udh': 'sudah',
    'udah': 'sudah',
    'sdh': 'sudah',
    'sdah': 'sudah',
    'dah': 'sudah',
    'org': 'orang',
    'orng': 'orang',
    'org2': 'orang-orang',
    'kyk': 'kayak',
    'kek': 'kayak',
    'ky': 'kayak',
    'emg': 'memang',
    'emng': 'memang',
    'mmg': 'memang',
    'aja': 'saja',
    'aj': 'saja',
    'doang': 'saja',
    'doank': 'saja',
    'dng': 'dong',
    'donk': 'dong',
    'sih': 'sih',
    'si': 'sih',
    'loh': 'lho',
    'lo': 'lho',
    'kok': 'kok',
    'knp': 'kenapa',
    'knapa': 'kenapa',
    'gmn': 'gimana',
    'gmna': 'gimana',
    'gmana': 'gimana',
    'bgmn': 'bagaimana',
    'apaan': 'apa',
    'apa2': 'apa-apa',
    'dmn': 'dimana',
    'dmna': 'dimana',
    'kpn': 'kapan',
    'kapn': 'kapan',
    'brp': 'berapa',
    'brapa': 'berapa',
    'lg': 'lagi',
    'lgi': 'lagi',
    'lg2': 'lagi-lagi',
    'pake': 'pakai',
    'pk': 'pakai',
    'pke': 'pakai',
    'bs': 'bisa',
    'bsa': 'bisa',
    'hrs': 'harus',
    'hrus': 'harus',
    'msh': 'masih',
    'msih': 'masih',
    'klo': 'kalau',
    'kalo': 'kalau',
    'kl': 'kalau',
    'ato': 'atau',
    'atw': 'atau',
    'dr': 'dari',
    'dri': 'dari',
    'pd': 'pada',
    'pda': 'pada',
    'ke': 'ke',
    'k': 'ke',
    'abis': 'habis',
    'abs': 'habis',
    'hbs': 'habis',
    'btw': 'ngomong-ngomong',
    'fyi': 'untuk informasi',
    'thx': 'terima kasih',
    'tks': 'terima kasih',
    'mksh': 'terima kasih',
    'makasi': 'terima kasih',
    'makasih': 'terima kasih',
    'mksih': 'terima kasih',
    'pls': 'tolong',
    'pliss': 'tolong',
    'plisss': 'tolong',
    'gws': 'get well soon',
    'wkwk': 'haha',
    'wkwkwk': 'haha',
    'wkwkwkwk': 'haha',
    'hahaha': 'haha',
    'hahahaha': 'haha',
    'kwkwk': 'haha',
    'awkwk': 'haha',
    'xixi': 'haha',
    'hehe': 'haha',
    'hihi': 'haha',
    'hoho': 'haha',
    'huhu': 'sedih',
    'hiks': 'sedih'
}


def remove_emojis(text: str) -> str:
    """Remove emojis from text"""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def remove_urls(text: str) -> str:
    """Remove URLs from text"""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub('', text)


def remove_mentions(text: str) -> str:
    """Remove @mentions from text"""
    return re.sub(r'@\w+', '', text)


def remove_hashtags(text: str) -> str:
    """Remove #hashtags from text"""
    return re.sub(r'#\w+', '', text)


def remove_numbers(text: str) -> str:
    """Remove standalone numbers"""
    return re.sub(r'\b\d+\b', '', text)


def remove_extra_whitespace(text: str) -> str:
    """Remove extra whitespace and normalize spaces"""
    return ' '.join(text.split())


def normalize_slang(text: str) -> str:
    """Normalize Indonesian slang words"""
    words = text.split()
    normalized = []
    for word in words:
        lower_word = word.lower()
        if lower_word in SLANG_DICT:
            normalized.append(SLANG_DICT[lower_word])
        else:
            normalized.append(word)
    return ' '.join(normalized)


def clean_text(text: str, normalize: bool = True) -> str:
    """
    Full text cleaning pipeline
    
    Args:
        text: Raw comment text
        normalize: Whether to normalize slang words
    
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = remove_urls(text)
    
    # Remove mentions
    text = remove_mentions(text)
    
    # Remove hashtags (keep the word, remove #)
    text = re.sub(r'#(\w+)', r'\1', text)
    
    # Remove emojis
    text = remove_emojis(text)
    
    # Remove special characters but keep Indonesian characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove numbers
    text = remove_numbers(text)
    
    # Normalize slang
    if normalize:
        text = normalize_slang(text)
    
    # Remove extra whitespace
    text = remove_extra_whitespace(text)
    
    return text.strip()


def clean_batch(texts: List[str], normalize: bool = True) -> List[str]:
    """Clean a batch of texts"""
    return [clean_text(t, normalize) for t in texts]


def tokenize(text: str) -> List[str]:
    """Simple tokenization by whitespace"""
    return text.split()


def get_word_frequencies(texts: List[str]) -> dict:
    """Get word frequencies from a list of texts"""
    freq = {}
    for text in texts:
        words = tokenize(text)
        for word in words:
            if len(word) > 2:  # Skip very short words
                freq[word] = freq.get(word, 0) + 1
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
