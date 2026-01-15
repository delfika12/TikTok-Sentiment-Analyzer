"""Quick test for sentiment analysis"""
from sentiment import analyze_batch

results = analyze_batch(['Bagus banget!', 'Jelek parah', 'Biasa aja'])
print('Test Results:')
for r in results:
    print(f"  {r['sentiment_label']:>8}: {r['original_text']}")
