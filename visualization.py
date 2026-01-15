"""
Visualization Module for TikTok Sentiment Analyzer
Creates charts, word clouds, and other visualizations
"""

import matplotlib.pyplot as plt
import matplotlib
from wordcloud import WordCloud
from typing import List, Dict, Optional
import io
import base64

# Use non-interactive backend for Streamlit
matplotlib.use('Agg')

# Color scheme
COLORS = {
    'positive': '#22c55e',  # Green
    'negative': '#ef4444',  # Red
    'neutral': '#6b7280',   # Gray
    'background': '#1e1e1e',
    'text': '#ffffff'
}


def create_sentiment_pie(positive: int, negative: int, neutral: int,
                         figsize: tuple = (8, 6)) -> plt.Figure:
    """
    Create pie chart for sentiment distribution
    
    Args:
        positive: Count of positive comments
        negative: Count of negative comments
        neutral: Count of neutral comments
        figsize: Figure size
    
    Returns:
        Matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor='#0e1117')
    ax.set_facecolor('#0e1117')
    
    # Data
    sizes = [positive, negative, neutral]
    labels = ['Positif', 'Negatif', 'Netral']
    colors = [COLORS['positive'], COLORS['negative'], COLORS['neutral']]
    explode = (0.02, 0.02, 0.02)
    
    # Filter out zero values
    non_zero = [(s, l, c, e) for s, l, c, e in zip(sizes, labels, colors, explode) if s > 0]
    if not non_zero:
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center', 
                fontsize=16, color=COLORS['text'])
        return fig
    
    sizes, labels, colors, explode = zip(*non_zero)
    
    # Create pie
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels,
        colors=colors,
        explode=explode,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'color': COLORS['text'], 'fontsize': 12}
    )
    
    # Style
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Distribusi Sentimen', color=COLORS['text'], fontsize=16, pad=20)
    
    plt.tight_layout()
    return fig


def create_sentiment_bar(positive: int, negative: int, neutral: int,
                         figsize: tuple = (10, 5)) -> plt.Figure:
    """
    Create horizontal bar chart for sentiment comparison
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor='#0e1117')
    ax.set_facecolor('#0e1117')
    
    categories = ['Positif', 'Negatif', 'Netral']
    values = [positive, negative, neutral]
    colors = [COLORS['positive'], COLORS['negative'], COLORS['neutral']]
    
    bars = ax.barh(categories, values, color=colors, height=0.6)
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(val), va='center', color=COLORS['text'], fontsize=12)
    
    ax.set_xlabel('Jumlah Komentar', color=COLORS['text'])
    ax.set_title('Perbandingan Sentimen', color=COLORS['text'], fontsize=16)
    
    # Style axes
    ax.tick_params(colors=COLORS['text'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['text'])
    ax.spines['left'].set_color(COLORS['text'])
    
    plt.tight_layout()
    return fig


def create_wordcloud(word_freq: Dict[str, int], 
                     colormap: str = 'viridis',
                     figsize: tuple = (12, 6),
                     max_words: int = 100) -> plt.Figure:
    """
    Create word cloud from word frequencies
    
    Args:
        word_freq: Dictionary of word: frequency
        colormap: Matplotlib colormap name
        figsize: Figure size
        max_words: Maximum words to show
    
    Returns:
        Matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor='#0e1117')
    ax.set_facecolor('#0e1117')
    
    if not word_freq:
        ax.text(0.5, 0.5, 'Tidak ada data kata', ha='center', va='center',
                fontsize=16, color=COLORS['text'])
        ax.axis('off')
        return fig
    
    # Create word cloud
    wc = WordCloud(
        width=1200,
        height=600,
        background_color='#0e1117',
        colormap=colormap,
        max_words=max_words,
        min_font_size=10,
        max_font_size=150,
        random_state=42
    ).generate_from_frequencies(word_freq)
    
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Word Cloud - Kata Populer', color=COLORS['text'], fontsize=16, pad=10)
    
    plt.tight_layout()
    return fig


def create_wordcloud_by_sentiment(results: List[Dict], 
                                  sentiment: str = 'positive') -> plt.Figure:
    """
    Create word cloud filtered by sentiment
    
    Args:
        results: Analysis results
        sentiment: 'positive', 'negative', or 'neutral'
    
    Returns:
        Matplotlib Figure
    """
    from utils import tokenize
    
    word_freq = {}
    for result in results:
        if result['sentiment_label'] == sentiment:
            words = tokenize(result['cleaned_text'])
            for word in words:
                if len(word) > 2:
                    word_freq[word] = word_freq.get(word, 0) + 1
    
    colormap = {
        'positive': 'Greens',
        'negative': 'Reds',
        'neutral': 'Greys'
    }.get(sentiment, 'viridis')
    
    return create_wordcloud(word_freq, colormap=colormap)


def create_score_histogram(results: List[Dict], 
                           figsize: tuple = (10, 5)) -> plt.Figure:
    """
    Create histogram of sentiment scores
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor='#0e1117')
    ax.set_facecolor('#0e1117')
    
    scores = [r['sentiment_score'] for r in results]
    
    if not scores:
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                fontsize=16, color=COLORS['text'])
        return fig
    
    # Create histogram
    n, bins, patches = ax.hist(scores, bins=20, edgecolor='white', alpha=0.7)
    
    # Color bars based on sentiment
    for i, patch in enumerate(patches):
        bin_center = (bins[i] + bins[i+1]) / 2
        if bin_center > 0.1:
            patch.set_facecolor(COLORS['positive'])
        elif bin_center < -0.1:
            patch.set_facecolor(COLORS['negative'])
        else:
            patch.set_facecolor(COLORS['neutral'])
    
    # Add vertical lines for thresholds
    ax.axvline(x=0.1, color='green', linestyle='--', alpha=0.5, label='Threshold Positif')
    ax.axvline(x=-0.1, color='red', linestyle='--', alpha=0.5, label='Threshold Negatif')
    
    ax.set_xlabel('Skor Sentimen', color=COLORS['text'])
    ax.set_ylabel('Jumlah Komentar', color=COLORS['text'])
    ax.set_title('Distribusi Skor Sentimen', color=COLORS['text'], fontsize=16)
    
    ax.tick_params(colors=COLORS['text'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['text'])
    ax.spines['left'].set_color(COLORS['text'])
    
    ax.legend(facecolor='#0e1117', labelcolor=COLORS['text'])
    
    plt.tight_layout()
    return fig


def fig_to_base64(fig: plt.Figure) -> str:
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# Quick test
if __name__ == "__main__":
    print("Testing visualizations...")
    
    # Test pie chart
    fig = create_sentiment_pie(45, 30, 25)
    fig.savefig('test_pie.png', facecolor=fig.get_facecolor())
    print("Created test_pie.png")
    
    # Test word cloud
    word_freq = {
        'bagus': 50, 'keren': 40, 'mantap': 35, 'recommended': 30,
        'jelek': 20, 'kecewa': 15, 'biasa': 25, 'worth': 28
    }
    fig = create_wordcloud(word_freq)
    fig.savefig('test_wordcloud.png', facecolor=fig.get_facecolor())
    print("Created test_wordcloud.png")
    
    plt.close('all')
    print("Done!")
