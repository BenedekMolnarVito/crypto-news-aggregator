# API Documentation

Complete API reference for the Crypto News Aggregator microservices.

## Table of Contents

1. [Scraper Service API](#scraper-service-api)
2. [Sentiment Analysis API](#sentiment-analysis-api)
3. [Django Web API](#django-web-api)

---

## Scraper Service API

**Base URL**: `http://localhost:5000`

### Health Check

**Endpoint**: `GET /health`

**Description**: Check if the scraper service is running

**Response**:
```json
{
  "status": "healthy",
  "service": "scraper"
}
```

### Scrape All Sources

**Endpoint**: `GET /scrape`

**Description**: Scrape latest 5 articles from all sources (CoinDesk, CoinTelegraph, Yahoo Finance)

**Response**:
```json
{
  "success": true,
  "count": 15,
  "articles": [
    {
      "source": "CoinDesk",
      "title": "Bitcoin Price Rises...",
      "url": "https://www.coindesk.com/...",
      "text": "Article content...",
      "scraped_at": "2025-10-22T15:00:00.000000"
    }
  ]
}
```

### Scrape CoinDesk

**Endpoint**: `GET /scrape/coindesk`

**Description**: Scrape latest 5 articles from CoinDesk only

**Response**: Same format as `/scrape`

### Scrape CoinTelegraph

**Endpoint**: `GET /scrape/cointelegraph`

**Description**: Scrape latest 5 articles from CoinTelegraph only

**Response**: Same format as `/scrape`

### Scrape Yahoo Finance

**Endpoint**: `GET /scrape/yahoo`

**Description**: Scrape latest 5 articles from Yahoo Finance Crypto only

**Response**: Same format as `/scrape`

---

## Sentiment Analysis API

**Base URL**: `http://localhost:8000`

**Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)

### Health Check

**Endpoint**: `GET /health`

**Description**: Check if the sentiment analysis service is running

**Response**:
```json
{
  "status": "healthy",
  "service": "sentiment_analysis"
}
```

### Analyze Multiple Articles

**Endpoint**: `POST /analyze`

**Description**: Analyze sentiment of multiple crypto news articles using LLM

**Request Body**:
```json
{
  "articles": [
    {
      "title": "Bitcoin Surges to New High",
      "text": "Bitcoin reached a new all-time high today...",
      "source": "CoinDesk",
      "url": "https://..."
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "title": "Bitcoin Surges to New High",
      "sentiment": "positive",
      "confidence": 0.85,
      "summary": "Bitcoin shows strong bullish momentum...",
      "key_points": [
        "Bitcoin reached new all-time high",
        "Institutional interest increasing",
        "Market sentiment strongly positive"
      ]
    }
  ],
  "overall_sentiment": "bullish",
  "market_outlook": "Market sentiment is predominantly positive based on recent news."
}
```

### Analyze Single Article

**Endpoint**: `POST /analyze/single`

**Description**: Analyze sentiment of a single article

**Request Body**:
```json
{
  "title": "Ethereum Network Upgrade Complete",
  "text": "The Ethereum network successfully completed its latest upgrade...",
  "source": "CoinTelegraph",
  "url": "https://..."
}
```

**Response**:
```json
{
  "success": true,
  "title": "Ethereum Network Upgrade Complete",
  "sentiment": "positive",
  "confidence": 0.78,
  "summary": "Ethereum upgrade successful, showing network maturity...",
  "key_points": [
    "Upgrade completed successfully",
    "Network stability improved",
    "Developer confidence high"
  ],
  "raw_analysis": "Full LLM response text..."
}
```

### List Available Models

**Endpoint**: `GET /models`

**Description**: Get information about available Ollama models

**Response**:
```json
{
  "current_model": "llama2",
  "available_models": [
    "llama2",
    "mistral",
    "mixtral",
    "neural-chat"
  ]
}
```

---

## Django Web API

**Base URL**: `http://localhost:8080`

### Trigger News Scraping

**Endpoint**: `POST /api/scrape/`

**Description**: Trigger scraping of news from all sources and save to database

**Headers**: Requires CSRF token (use from browser or Django session)

**Response**:
```json
{
  "success": true,
  "message": "Successfully scraped 15 articles",
  "count": 15
}
```

### Trigger Sentiment Analysis

**Endpoint**: `POST /api/analyze/`

**Description**: Analyze sentiment of unanalyzed articles in database

**Headers**: Requires CSRF token

**Response**:
```json
{
  "success": true,
  "message": "Analyzed 10 articles",
  "count": 10
}
```

### List Articles

**Endpoint**: `GET /api/articles/`

**Description**: Get list of scraped articles from database

**Response**:
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Bitcoin Price Analysis",
      "source": "coindesk",
      "url": "https://...",
      "sentiment": "positive",
      "confidence": 0.82,
      "scraped_at": "2025-10-22T15:00:00.000000"
    }
  ]
}
```

### Get Sentiment Statistics

**Endpoint**: `GET /api/stats/`

**Description**: Get aggregated sentiment statistics

**Response**:
```json
{
  "total_articles": 50,
  "sentiment_distribution": {
    "positive": 30,
    "negative": 10,
    "neutral": 10
  },
  "latest_analysis": {
    "date": "2025-10-22",
    "overall_sentiment": "bullish",
    "market_outlook": "Market sentiment is predominantly positive..."
  }
}
```

---

## Error Responses

All APIs use standard HTTP status codes and return errors in this format:

```json
{
  "success": false,
  "error": "Error description"
}
```

Common status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider:
- Adding rate limiting middleware
- Implementing API key authentication
- Using request throttling

---

## Authentication

Current implementation:
- Scraper API: No authentication required
- Sentiment API: No authentication required
- Django API: CSRF protection for POST requests

For production, consider:
- API key authentication
- OAuth2 implementation
- JWT tokens for API access

---

## Best Practices

1. **Batch Processing**: Use the batch analyze endpoint for multiple articles
2. **Error Handling**: Always check the `success` field in responses
3. **Logging**: Monitor logs for debugging issues
4. **Caching**: Consider caching frequently accessed data
5. **Async Operations**: Use async endpoints for long-running operations

---

## Examples with cURL

### Scrape all news sources
```bash
curl http://localhost:5000/scrape
```

### Analyze article sentiment
```bash
curl -X POST http://localhost:8000/analyze/single \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Crypto Market Analysis",
    "text": "The cryptocurrency market shows strong growth..."
  }'
```

### Get sentiment statistics
```bash
curl http://localhost:8080/api/stats/
```

---

## Examples with Python

```python
import requests

# Scrape news
response = requests.get('http://localhost:5000/scrape')
articles = response.json()['articles']

# Analyze sentiment
data = {
    "articles": [
        {
            "title": article["title"],
            "text": article["text"]
        } for article in articles
    ]
}
response = requests.post('http://localhost:8000/analyze', json=data)
results = response.json()

# Get statistics
response = requests.get('http://localhost:8080/api/stats/')
stats = response.json()
print(f"Total articles: {stats['total_articles']}")
```

---

## WebSocket Support

Currently not implemented. Future versions may include:
- Real-time article updates
- Live sentiment analysis streams
- Push notifications for market changes
