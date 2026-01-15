"""
Database module for TikTok Sentiment Analyzer
Handles SQLite operations for storing search sessions, comments, and videos
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sentiment.db')


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database and create tables if not exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create search_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            total_comments INTEGER DEFAULT 0,
            positive_count INTEGER DEFAULT 0,
            negative_count INTEGER DEFAULT 0,
            neutral_count INTEGER DEFAULT 0,
            avg_sentiment_score REAL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            video_url TEXT,
            username TEXT,
            comment_text TEXT,
            cleaned_text TEXT,
            sentiment_score REAL,
            sentiment_label TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions(id)
        )
    ''')
    
    # Create videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            video_url TEXT,
            video_title TEXT,
            author TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()


def save_session(keyword: str, total_comments: int, positive_count: int,
                 negative_count: int, neutral_count: int, 
                 avg_sentiment_score: float) -> int:
    """
    Save a new search session and return its ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO search_sessions 
        (keyword, total_comments, positive_count, negative_count, neutral_count, avg_sentiment_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (keyword, total_comments, positive_count, negative_count, neutral_count, avg_sentiment_score))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return session_id


def save_comments(session_id: int, comments: List[Dict]) -> None:
    """
    Bulk insert comments for a session
    comments: List of dicts with keys: video_url, username, comment_text, 
              cleaned_text, sentiment_score, sentiment_label
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT INTO comments 
        (session_id, video_url, username, comment_text, cleaned_text, sentiment_score, sentiment_label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [(
        session_id,
        c.get('video_url', ''),
        c.get('username', ''),
        c.get('comment_text', ''),
        c.get('cleaned_text', ''),
        c.get('sentiment_score', 0),
        c.get('sentiment_label', 'neutral')
    ) for c in comments])
    
    conn.commit()
    conn.close()


def save_videos(session_id: int, videos: List[Dict]) -> None:
    """
    Save video information for a session
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT INTO videos 
        (session_id, video_url, video_title, author, likes_count, comments_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [(
        session_id,
        v.get('video_url', ''),
        v.get('video_title', ''),
        v.get('author', ''),
        v.get('likes_count', 0),
        v.get('comments_count', 0)
    ) for v in videos])
    
    conn.commit()
    conn.close()


def get_history(limit: int = 20) -> List[Dict]:
    """
    Get recent search history
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, keyword, total_comments, positive_count, negative_count, 
               neutral_count, avg_sentiment_score, created_at
        FROM search_sessions
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_session_detail(session_id: int) -> Optional[Dict]:
    """
    Get detailed information about a specific session
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute('''
        SELECT * FROM search_sessions WHERE id = ?
    ''', (session_id,))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        return None
    
    # Get comments
    cursor.execute('''
        SELECT * FROM comments WHERE session_id = ?
    ''', (session_id,))
    comments = cursor.fetchall()
    
    # Get videos
    cursor.execute('''
        SELECT * FROM videos WHERE session_id = ?
    ''', (session_id,))
    videos = cursor.fetchall()
    
    conn.close()
    
    return {
        'session': dict(session),
        'comments': [dict(c) for c in comments],
        'videos': [dict(v) for v in videos]
    }


def get_session_comments(session_id: int) -> List[Dict]:
    """Get all comments for a session"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM comments WHERE session_id = ? ORDER BY id
    ''', (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def delete_session(session_id: int) -> bool:
    """Delete a session and all related data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM comments WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM videos WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM search_sessions WHERE id = ?', (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False


# Initialize database on module import
init_db()
