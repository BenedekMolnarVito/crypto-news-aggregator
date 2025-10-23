# Quick Start Guide

This guide will help you get the Crypto News Aggregator up and running quickly.

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.11+ installed

## Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/BenedekMolnarVito/crypto-news-aggregator.git
   cd crypto-news-aggregator
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure your settings:
   ```bash
   # Ollama API
   OLLAMA_API_URL=https://api.ollama.ai/api/generate
   OLLAMA_MODEL=llama2
   
   # Database
   DB_NAME=crypto_news
   DB_USER=user
   DB_PASSWORD=postgres
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Web Dashboard: http://localhost:8080
   - Scraper API Docs: http://localhost:5000/health
   - Sentiment API Docs: http://localhost:8000/docs

5. **Use the dashboard**
   - Click "Scrape Latest News" to collect articles
   - Click "Analyze Sentiment" to run LLM analysis
   - View sentiment statistics and market outlook

## Quick Start without Docker

### 1. Set up Scraper Service

```bash
cd scraper_service
pip install -r requirements.txt
python app.py
```

The scraper service will be available at http://localhost:5000

### 2. Set up Sentiment Analysis Service

Open a new terminal:

```bash
cd llm_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

The sentiment API will be available at http://localhost:8000

### 3. Set up PostgreSQL Database

First, install and start PostgreSQL:

```bash
# For Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb crypto_news
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

### 4. Set up Django Web Application

Open another terminal:

```bash
cd django_app
pip install -r requirements.txt

# Set environment variables
export DB_NAME=crypto_news
export DB_USER=user
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432

# Run migrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser

# Start the server
python manage.py runserver 0.0.0.0:8080
```

The web application will be available at http://localhost:8080

**Note:** For development without Docker, you can also use SQLite by modifying the DATABASES setting in `django_app/crypto_sentiment/settings.py`.

## Using the API

### Scraper API Examples

```bash
# Check service health
curl http://localhost:5000/health

# Scrape all sources
curl http://localhost:5000/scrape

# Scrape specific source
curl http://localhost:5000/scrape/coindesk
curl http://localhost:5000/scrape/cointelegraph
curl http://localhost:5000/scrape/yahoo
```

### Sentiment Analysis API Examples

```bash
# Check service health
curl http://localhost:8000/health

# Analyze a single article
curl -X POST http://localhost:8000/analyze/single \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bitcoin Surges to New High",
    "text": "Bitcoin reached a new all-time high today as institutional investors continue to show strong interest in cryptocurrency markets..."
  }'

# List available models
curl http://localhost:8000/models
```

### Django API Examples

```bash
# Get sentiment statistics
curl http://localhost:8080/api/stats/

# Get articles list
curl http://localhost:8080/api/articles/

# Trigger scraping (requires CSRF token from browser)
curl -X POST http://localhost:8080/api/scrape/

# Trigger sentiment analysis (requires CSRF token from browser)
curl -X POST http://localhost:8080/api/analyze/
```

## Accessing the Admin Panel

1. Create a superuser (if not already done):
   ```bash
   cd django_app
   python manage.py createsuperuser
   ```

2. Navigate to http://localhost:8080/admin

3. Log in with your superuser credentials

4. Manage articles and sentiment analyses

## Configuring Ollama

### Using Ollama Cloud

Set these environment variables in `.env`:
```bash
OLLAMA_API_URL=https://api.ollama.ai/api/generate
OLLAMA_MODEL=llama2
```

### Using Local Ollama

1. Install Ollama locally: https://ollama.ai

2. Pull a model:
   ```bash
   ollama pull llama2
   ```

3. Update `.env`:
   ```bash
   OLLAMA_API_URL=http://localhost:11434/api/generate
   OLLAMA_MODEL=llama2
   ```

## Troubleshooting

### Services won't start

- Check if ports 5000, 8000, and 8080 are available
- Ensure all dependencies are installed correctly
- Check Docker logs: `docker-compose logs -f`

### No articles are scraped

- This is expected in restricted network environments
- The scraper requires internet access to crypto news sites
- Check scraper logs for specific errors

### Sentiment analysis fails

- Verify Ollama API configuration
- Check if the Ollama service is accessible
- Review FastAPI logs for errors

### Database errors

- Run migrations: `python manage.py migrate`
- Delete `db.sqlite3` and run migrations again if needed

## Next Steps

- Customize scraping sources in `scraper_service/scraper.py`
- Adjust sentiment prompts in `llm_service/main.py`
- Modify the dashboard UI in `django_app/news/templates/news/dashboard.html`
- Add scheduled scraping with cron jobs or Celery
- Deploy to production with proper secret management

## Support

For issues and questions:
- Check the main README.md
- Review the code documentation
- Open an issue on GitHub
