# TikTok Sentiment Analyzer

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white) 
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) 
![Apify](https://img.shields.io/badge/Apify-Scraper-96E072?style=flat-square&logo=apify&logoColor=black)
![Status](https://img.shields.io/badge/Status-Active-22c55e?style=flat-square)

A local desktop application for **real-time TikTok Comment Sentiment Analysis**. This tool facilitates data extraction from TikTok videos, performs sentiment analysis (Positive/Negative/Neutral) using a lexicon-based approach optimized for Indonesian language, and visualizes the results through interactive dashboards.

---

## Application Preview

![Dashboard UI](assets/app_screenshot.png)

*Interactive dashboard featuring sentiment distribution charts, word clouds, and detailed data tables.*

---

## Key Features

- **Real-time Scraping**: Integrated with **Apify** to extract hundreds of comments efficiently.
- **Indonesian Sentiment Analysis**: Utilizes a **Lexicon-based** method optimized for Indonesian slang and context (e.g., handling terms like "gacor", "zonk", "worth it").
- **Data Visualization**:
  - **Pie Chart**: Sentiment percentage distribution.
  - **Word Cloud**: Visual representation of frequently used words.
  - **Histogram**: Sentiment score distribution.
- **Local Database**: All analysis results are automatically stored in **SQLite** for historical tracking.
- **Streamlined UI**: Clean, professional interface designed for ease of use without complex attributes.

---

## Technology Stack

| Component | Technology | Description |
| --- | --- | --- |
| **Framework** | **Streamlit** | Python-based interactive web framework |
| **Scraper** | **Apify Client** | Reliable TikTok data extraction |
| **Database** | **SQLite** | Serverless, self-contained SQL database engine |
| **Visualization** | **Matplotlib** | Static, animated, and interactive visualizations |
| **Processing** | **Pandas** | Data manipulation and analysis library |

---

## Installation Guide

### Prerequisites
1. **Python 3.10+** installed.
2. **[Apify](https://apify.com/)** account for API Token access.

### Steps
1. **Clone Repository**
   ```bash
   git clone https://github.com/delfika12/TikTok-Sentiment-Analyzer.git
   cd TikTok-Sentiment-Analyzer
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**
   ```bash
   streamlit run app.py
   ```

---

## Usage Instructions

1. **Configure Apify Token** (First time only):
   - Navigate to **Settings** in the sidebar.
   - Enter your **Apify API Token**.
2. **Start Analysis**:
   - Go to **Analisis Baru** menu.
   - Enter **Topic Name**.
   - Input **TikTok Video URL**.
   - Click **Start Scraping & Analyze**.
3. **View Results**:
   - Wait for the process to complete.
   - The dashboard will present sentiment charts and comment tables.

---

## Project Structure

```
TikTok-Sentiment-Analyzer/
├── app.py                # Main Application Entry Point
├── scraper.py            # Apify Integration Module
├── sentiment.py          # Sentiment Analysis Logic
├── database.py           # SQLite Database Operations
├── visualization.py      # Charting & WordCloud Generation
├── utils.py              # Text Preprocessing Utilities
├── assets/
│   ├── lexicon_id.json   # Indonesian Sentiment Lexicon
│   └── app_screenshot.png
├── data/
│   └── sentiment.db      # Local Database File
└── requirements.txt      # Project Dependencies
```

---

## Disclaimer
- This application requires an internet connection for scraping via Apify.
- Ensure you have sufficient Apify credits (Free tier is usually sufficient for testing).
- Sentiment lexicon can be customized in `assets/lexicon_id.json`.

---

**Author**: Delfika
