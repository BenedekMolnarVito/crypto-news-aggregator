# Crypto News Aggregator

This is an LLM-based web app that collects, aggregates and analyzes crypto market sentiment based on news articles from various crypto sites and exchanges.

## Features

🚀 **One-Page Catchy UI** with three main functionalities:

1. **📰 Web Scraping** - Scrapes latest crypto news from multiple sources
2. **📊 Sentiment Analysis** - Uses Ollama AI to analyze market sentiment based on scraped news
3. **💰 Price Predictions** - Uses Ollama AI to predict next-day prices for BTC, ETH, and SOL

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running (for AI features)
  - Install from: https://ollama.ai
  - Run: `ollama pull llama3.2` to download the model

## Installation

1. Clone the repository:
```bash
git clone https://github.com/BenedekMolnarVito/crypto-news-aggregator.git
cd crypto-news-aggregator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is running:
```bash
ollama serve
```

## Running the Application

Start the Flask web server:
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Usage

1. **Scrape Latest News**: Click the "📰 Scrape Latest News" button to fetch the latest crypto news headlines
2. **Analyze Sentiment**: After scraping news, click "📊 Analyze Market Sentiment" to get an AI-powered sentiment analysis
3. **Predict Prices**: Click "💰 Predict Prices (BTC, ETH, SOL)" to get next-day price predictions for Bitcoin, Ethereum, and Solana

## Tech Stack

- **Backend**: Flask (Python)
- **Web Scraping**: BeautifulSoup4, Requests
- **AI Integration**: Ollama API (llama3.2 model)
- **Frontend**: HTML, CSS, JavaScript
- **UI Design**: Modern gradient design with smooth animations

## Notes

- The sentiment analysis and price predictions require Ollama to be running locally
- If Ollama is not available, you'll see appropriate error messages
- The web scraping uses fallback data if live scraping fails
- All AI prompts are hardcoded as per requirements
