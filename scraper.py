"""
TikTok Scraper Module using Apify
Handles fetching comments from TikTok using Apify Client
"""

from apify_client import ApifyClient
from typing import List, Dict, Optional
import os

# Default Actor ID for TikTok Comment Scraper
# Using 'clockworks/tiktok-comments-scraper' which is a popular choice
# Alternative: 'mojura/tiktok-comment-scraper'
ACTOR_ID = "clockworks/tiktok-comments-scraper"

def scrape_comments_apify(
    video_url: str, 
    api_token: str, 
    max_comments: int = 100
) -> Dict:
    """
    Scrape TikTok comments using Apify
    
    Args:
        video_url: URL of the TikTok video
        api_token: Apify API Token
        max_comments: Maximum number of comments to retrieve
        
    Returns:
        Dict containing list of comments and video metadata
    """
    if not api_token:
        raise ValueError("Apify API Token is required")

    print(f"Starting Apify scraper for {video_url}...")
    
    # Initialize the ApifyClient with the API token
    client = ApifyClient(api_token)

    # Prepare the Actor input
    run_input = {
        "postURLs": [video_url],
        "commentsPerPost": max_comments,
    }

    # Run the Actor and wait for it to finish
    # This can take time depending on the amount of data
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    
    print(f"Actor run finished. ID: {run['id']}")

    # Fetch and print Actor results from the run's dataset (if there are any)
    comments = []
    
    # Default metadata in case not found
    video_meta = {
        'video_url': video_url,
        'video_title': 'TikTok Video',
        'author': 'Unknown',
        'likes_count': 0,
        'comments_count': 0
    }
    
    # Iterate over the items in the dataset
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        # Clean up and normalize data structure
        text = item.get('text', '')
        if not text:
            continue
            
        comments.append({
            'comment_text': text,
            'username': item.get('author', {}).get('uniqueId', 'user'),
            'video_url': video_url,
            # Apify specific fields might vary, trying to be safe
            'likes_count': item.get('diggCount', 0),
            'reply_count': item.get('replyCount', 0),
            'created_at': item.get('createTimeISO', '')
        })

    print(f"Fetched {len(comments)} comments.")
    
    return {
        'videos': [video_meta], # Apify comment scraper might not return full video details, usually mostly comments
        'comments': comments
    }

# Function for testing
if __name__ == "__main__":
    # Test with a dummy token or prompt user
    token = os.environ.get("APIFY_TOKEN")
    if token:
        res = scrape_comments_apify("https://www.tiktok.com/@...", token, 10)
        print(f"Found {len(res['comments'])} comments")
    else:
        print("Set APIFY_TOKEN env var to test")
