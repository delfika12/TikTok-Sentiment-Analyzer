"""
TikTok Sentiment Analyzer - Main Streamlit Application

╔══════════════════════════════════════════════════════════════════════════╗
║                     TIKTOK SENTIMENT ANALYZER                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ┌─────────────────────┐  ┌─────────────────────────────────────────┐   ║
║  │ 🔍 Analisis Baru    │  │  Tabs: [Manual] [CSV] [Apify Scraper]   │   ║
║  │                     │  │                                         │   ║
║  │ 📊 History          │  │  [Apify] URL Video: _________________   │   ║
║  │                     │  │          Limit: 100                     │   ║
║  │ ⚙️ Settings         │  │                                         │   ║
║  │                     │  │  [🚀 MULAI ANALISIS]                    │   ║
║  └─────────────────────┘  └─────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Import local modules
from database import (
    init_db, save_session, save_comments,
    get_history, get_session_detail, delete_session
)
from scraper import scrape_comments_apify
from sentiment import analyze_batch, get_sentiment_summary, get_top_words
from visualization import (
    create_sentiment_pie, create_sentiment_bar,
    create_wordcloud, create_score_histogram
)
from utils import clean_text, get_word_frequencies

# Page configuration
st.set_page_config(
    page_title="TikTok Sentiment Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff0050;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #333;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff0050;
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #d60043;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'analyze'
    if 'apify_token' not in st.session_state:
        st.session_state.apify_token = ""


def show_analysis_page():
    """Main analysis page"""
    st.markdown('<h1 class="main-header">📊 TikTok Sentiment Analyzer</h1>', unsafe_allow_html=True)
    
    # Input section
    st.markdown("### 🔍 Analisis Baru")
    
    # Topic/keyword
    keyword = st.text_input(
        "Nama Topik/Produk",
        placeholder="Contoh: iPhone 16, Skincare viral, dll",
        help="Label untuk menyimpan hasil analisis"
    )
    
    st.markdown("---")
    st.info("Menggunakan **Apify** untuk scraping real-time.")
    
    # Check token
    if not st.session_state.apify_token:
        st.warning("⚠️ API Token belum diset! Masukkan di menu **Settings**.")
        st.text_input("Atau masukkan sementara di sini:", type="password", key="temp_token")
    
    apify_url = st.text_input(
        "URL Video TikTok",
        placeholder="https://www.tiktok.com/@user/video/1234567890"
    )
    
    max_comments = st.number_input("Maksimal Komentar", min_value=10, max_value=1000, value=100)
    
    if st.button("🚀 Start Scraping & Analyze", key="btn_apify"):
        token = st.session_state.apify_token or st.session_state.get("temp_token")
        if not token:
            st.error("Butuh Apify API Token!")
        elif not apify_url:
            st.error("Masukkan URL Video!")
        else:
            run_apify_analysis(keyword or "Apify Result", apify_url, token, max_comments)


def run_manual_analysis(keyword: str, comments_list: list):
    """Run analysis on manually provided comments"""
    with st.status("🔄 Sedang memproses...", expanded=True) as status:
        st.write(f"📝 Menganalisis {len(comments_list)} komentar...")
        time.sleep(0.3)
        
        # Analyze
        analysis_results = analyze_batch(comments_list)
        
        # Add metadata
        for i, result in enumerate(analysis_results):
            result['video_url'] = ''
            result['username'] = f'user_{i+1}'
            result['comment_text'] = comments_list[i]
        
        # Summary & Save
        summary = get_sentiment_summary(analysis_results)
        
        st.write("💾 Menyimpan hasil...")
        session_id = save_session(
            keyword=keyword,
            total_comments=summary['total'],
            positive_count=summary['positive_count'],
            negative_count=summary['negative_count'],
            neutral_count=summary['neutral_count'],
            avg_sentiment_score=summary['avg_score']
        )
        save_comments(session_id, analysis_results)
        
        st.session_state.analysis_results = {
            'keyword': keyword,
            'session_id': session_id,
            'summary': summary,
            'results': analysis_results,
            'videos': []
        }
        status.update(label="✅ Selesai!", state="complete", expanded=False)
    
    display_results()


def run_apify_analysis(keyword: str, url: str, token: str, max_comments: int):
    """Run extraction via Apify and analyze"""
    with st.status("🕷️ Menjalankan Apify Scraper...", expanded=True) as status:
        st.write("Menghubungkan ke Apify Cloud...")
        
        try:
            # Call Scraper
            result = scrape_comments_apify(url, token, max_comments)
            comments_data = result['comments']
            
            if not comments_data:
                st.error("Tidak ada komentar ditemukan atau akses ditolak.")
                status.update(label="❌ Gagal", state="error")
                return

            st.write(f"✅ Berhasil mengambil {len(comments_data)} komentar!")
            st.write("Menganalisis sentimen...")
            
            # Extract text
            texts = [c['comment_text'] for c in comments_data]
            sentiments = analyze_batch(texts)
            
            # Merge
            final_results = []
            for i, s in enumerate(sentiments):
                s.update(comments_data[i]) # Merge Apify data (username etc)
                final_results.append(s)
            
            # Save
            summary = get_sentiment_summary(final_results)
            session_id = save_session(
                keyword=keyword,
                total_comments=summary['total'],
                positive_count=summary['positive_count'],
                negative_count=summary['negative_count'],
                neutral_count=summary['neutral_count'],
                avg_sentiment_score=summary['avg_score']
            )
            save_comments(session_id, final_results)
            
            st.session_state.analysis_results = {
                'keyword': keyword,
                'session_id': session_id,
                'summary': summary,
                'results': final_results,
                'videos': [{'video_url': url, 'author': 'Apify'}]
            }
            
            status.update(label="✅ Selesai!", state="complete", expanded=False)
            
        except Exception as e:
            st.error(f"Apify Error: {str(e)}")
            status.update(label="❌ Error", state="error")
            return

    display_results()


def display_results():
    """Display analysis results"""
    if not st.session_state.analysis_results:
        return
    
    data = st.session_state.analysis_results
    summary = data['summary']
    results = data['results']
    
    st.markdown("---")
    st.markdown(f"### 📊 Hasil: `{data['keyword']}`")
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", summary['total'])
    c2.metric("✅ Positif", f"{summary['positive_count']} ({summary['positive_pct']}%)")
    c3.metric("❌ Negatif", f"{summary['negative_count']} ({summary['negative_pct']}%)")
    c4.metric("Skor", f"{summary['avg_score']:+.3f}")
    
    # Charts
    st.markdown("### 📈 Visualisasi")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(create_sentiment_pie(
            summary['positive_count'], summary['negative_count'], summary['neutral_count']
        ))
    with col2:
        wc_freq = get_word_frequencies([r['cleaned_text'] for r in results])
        if wc_freq:
            st.pyplot(create_wordcloud(wc_freq))
    
    # Table
    st.markdown("### 📝 Detail")
    df = pd.DataFrame([{
        'User': r.get('username', '-'),
        'Komentar': r.get('comment_text', ''),
        'Sentimen': r.get('sentiment_label', 'neutral'),
        'Skor': r.get('sentiment_score', 0)
    } for r in results])
    st.dataframe(df, use_container_width=True)


def show_history_page():
    """History page"""
    st.markdown("### 📊 Riwayat")
    history = get_history(20)
    for item in history:
        with st.expander(f"{item['created_at']} - {item['keyword']}"):
            if st.button("Load", key=f"load_{item['id']}"):
                detail = get_session_detail(item['id'])
                if detail:
                    st.session_state.analysis_results = {
                        'keyword': item['keyword'],
                        'session_id': item['id'],
                        'summary': get_sentiment_summary(detail['comments']), # re-calc summary or use db
                        'results': detail['comments'],
                        'videos': detail['videos']
                    }
                    st.session_state.current_page = 'analyze'
                    st.rerun()
            if st.button("Delete", key=f"del_{item['id']}"):
                delete_session(item['id'])
                st.rerun()


def show_settings_page():
    """Settings page"""
    st.markdown("### ⚙️ Pengaturan")
    
    st.markdown("#### 🔑 Apify Configuration")
    token = st.text_input(
        "Apify API Token", 
        value=st.session_state.apify_token, 
        type="password",
        help="Dapatkan token di console.apify.com"
    )
    if token != st.session_state.apify_token:
        st.session_state.apify_token = token
        st.success("Token saved to session!")

    st.markdown("---")
    st.markdown("#### 🗑️ Data Management")
    if st.button("Clear All Data"):
        st.warning("Not implemented for safety.")


def main():
    init_db()
    init_session_state()
    
    with st.sidebar:
        st.title("📱 Menu")
        if st.button("🔍 Analisis"): st.session_state.current_page = 'analyze'
        if st.button("📊 History"): st.session_state.current_page = 'history'
        if st.button("⚙️ Settings"): st.session_state.current_page = 'settings'
        
        if st.session_state.apify_token:
            st.success("✅ Apify Token Set")
        else:
            st.warning("⚠️ Apify Token Empty")

    if st.session_state.current_page == 'analyze':
        show_analysis_page()
        if st.session_state.analysis_results:
            display_results()
    elif st.session_state.current_page == 'history':
        show_history_page()
    elif st.session_state.current_page == 'settings':
        show_settings_page()

if __name__ == "__main__":
    main()
