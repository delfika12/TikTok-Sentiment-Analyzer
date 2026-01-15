# TikTok Sentiment Analyzer

Aplikasi analisis sentimen komentar TikTok berbasis lokal menggunakan Streamlit dan Apify.

## Fitur
- **Apify Integration**: Scraping komentar TikTok secara real-time.
- **Sentiment Analysis**: Menggunakan pendekatan Lexicon-based (Bahasa Indonesia).
- **Visualisasi**: Pie chart, Word Cloud, dan Histogram skor.
- **Database Lokal**: Menyimpan riwayat analisis menggunakan SQLite.

## Cara Instalasi

1. Clone repository ini
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup Apify:
   - Buat akun di [Apify](https://apify.com/)
   - Dapatkan API Token di Console
   - Masukkan token di menu Settings aplikasi

## Cara Menjalankan

```bash
streamlit run app.py
```

## Teknologi
- Python 3.12+
- Streamlit
- Matplotlib
- Apify Client
- SQLite
