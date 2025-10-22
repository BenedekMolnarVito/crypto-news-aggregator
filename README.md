# crypto-news-aggregator

An LLM-based Django web application that collects, aggregates, and analyzes crypto market sentiment based on news articles from various crypto sites and exchanges. Built with a modular microservice architecture following best practices.

## 🏗️ Architecture

This application follows a **microservice architecture** with three main services:

1. **Web Scraper Service** (Flask) - Port 5000
   - Scrapes latest crypto news from CoinDesk, CoinTelegraph, and Yahoo Finance
   - Provides REST API endpoints for triggering scraping operations
   - Extracts article titles, URLs, and full text content

2. **Sentiment Analysis Service** (FastAPI) - Port 8000
   - Uses Ollama Cloud LLM models for sentiment analysis
   - Analyzes crypto news articles for market sentiment
   - Provides structured sentiment data with confidence scores

3. **Web Application** (Django) - Port 8080
   - Main user interface and dashboard
   - Orchestrates scraper and sentiment services
   - Stores and manages articles in PostgreSQL database
   - Displays sentiment analysis results

## 🚀 Features

- **Multi-source News Scraping**: Collects latest 5 articles from each source:
  - CoinDesk (https://www.coindesk.com/)
  - CoinTelegraph (https://cointelegraph.com/)
  - Yahoo Finance Crypto (https://finance.yahoo.com/topic/crypto/)

- **LLM-based Sentiment Analysis**: Uses Ollama Cloud models to analyze:
  - Article sentiment (positive/negative/neutral)
  - Confidence scores
  - Key points and summaries
  - Overall market outlook

- **Interactive Dashboard**: 
  - Real-time sentiment statistics
  - Article management
  - One-click scraping and analysis
  - Beautiful, responsive UI

- **REST APIs**: 
  - Scraper API endpoints
  - Sentiment analysis API endpoints
  - Django API for data access

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional, for containerized deployment)
- Ollama Cloud API access (or local Ollama installation)

## 🛠️ Installation & Setup

### Option 1: Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/BenedekMolnarVito/crypto-news-aggregator.git
cd crypto-news-aggregator
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env and configure your Ollama API settings
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

4. Access the application:
   - Web Dashboard: http://localhost:8080
   - Scraper API: http://localhost:5000
   - Sentiment API: http://localhost:8000

### Option 2: Manual Setup

#### 1. Set up Web Scraper Service

```bash
cd scraper_service
pip install -r requirements.txt
python app.py
```

#### 2. Set up Sentiment Analysis Service

```bash
cd fastapi_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 3. Set up Django Web Application

```bash
cd django_app
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
python manage.py runserver 0.0.0.0:8080
```

## 📖 API Documentation

### Scraper Service API

**Base URL**: http://localhost:5000

- `GET /health` - Health check
- `GET /scrape` - Scrape all sources
- `GET /scrape/coindesk` - Scrape CoinDesk only
- `GET /scrape/cointelegraph` - Scrape CoinTelegraph only
- `GET /scrape/yahoo` - Scrape Yahoo Finance only

### Sentiment Analysis API

**Base URL**: http://localhost:8000

- `GET /health` - Health check
- `POST /analyze` - Analyze multiple articles
- `POST /analyze/single` - Analyze single article
- `GET /models` - List available models
- `GET /docs` - Interactive API documentation (Swagger UI)

### Django Web App API

**Base URL**: http://localhost:8080

- `GET /` - Dashboard view
- `POST /api/scrape/` - Trigger news scraping
- `POST /api/analyze/` - Trigger sentiment analysis
- `GET /api/articles/` - List articles
- `GET /api/stats/` - Get sentiment statistics

## 🎯 Usage

1. **Scrape News**: Click "Scrape Latest News" button on the dashboard to collect latest articles from all sources

2. **Analyze Sentiment**: Click "Analyze Sentiment" to run LLM-based sentiment analysis on scraped articles

3. **View Results**: The dashboard displays:
   - Total article count
   - Sentiment distribution (positive/negative/neutral)
   - Overall market outlook
   - Individual article sentiments with confidence scores

4. **Admin Panel**: Access Django admin at http://localhost:8080/admin for detailed data management

## 🏛️ Project Structure

```
crypto-news-aggregator/
├── scraper_service/          # Web scraper microservice
│   ├── scraper.py           # Scraping logic
│   ├── app.py               # Flask API
│   ├── requirements.txt     # Dependencies
│   └── Dockerfile           # Container configuration
│
├── fastapi_service/          # Sentiment analysis microservice
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Dependencies
│   └── Dockerfile           # Container configuration
│
├── django_app/               # Main web application
│   ├── crypto_sentiment/    # Django project settings
│   ├── news/                # News app
│   │   ├── models.py        # Database models
│   │   ├── views.py         # Views and API endpoints
│   │   ├── services.py      # Service integrations
│   │   ├── admin.py         # Admin configuration
│   │   └── templates/       # HTML templates
│   ├── manage.py            # Django management script
│   ├── requirements.txt     # Dependencies
│   └── Dockerfile           # Container configuration
│
├── docker-compose.yml        # Multi-service orchestration
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

- `OLLAMA_API_URL`: URL for Ollama API (default: https://api.ollama.ai/api/generate)
- `OLLAMA_MODEL`: LLM model to use (default: llama2)
- `SCRAPER_SERVICE_URL`: Scraper service URL
- `SENTIMENT_SERVICE_URL`: Sentiment service URL
- `DEBUG`: Django debug mode
- `SECRET_KEY`: Django secret key (change in production!)

## 🔒 Security Considerations

- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints
- Use HTTPS in production
- Regularly update dependencies

## 🧪 Testing

Each service can be tested independently:

```bash
# Test scraper service
curl http://localhost:5000/scrape

# Test sentiment service
curl -X POST http://localhost:8000/analyze/single \
  -H "Content-Type: application/json" \
  -d '{"title":"Bitcoin rises","text":"Bitcoin price increased today..."}'

# Test Django API
curl http://localhost:8080/api/stats/
```

## 📝 Development

### Adding New News Sources

1. Add source URL to `scraper_service/scraper.py`
2. Implement scraping method
3. Update source choices in Django models
4. Add source-specific endpoint in Flask API

### Customizing Sentiment Analysis

1. Modify prompts in `fastapi_service/main.py`
2. Change Ollama model in environment variables
3. Adjust parsing logic for different response formats

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- News sources: CoinDesk, CoinTelegraph, Yahoo Finance
- LLM provider: Ollama
- Frameworks: Django, FastAPI, Flask
- Beautiful UI inspired by modern dashboard designs

