# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Crypto News Aggregator System                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                           External Sources                           │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│   CoinDesk      │  CoinTelegraph  │    Yahoo Finance Crypto         │
│ www.coindesk.com│ cointelegraph.  │  finance.yahoo.com/topic/crypto │
│                 │      com        │                                 │
└────────┬────────┴────────┬────────┴──────────┬──────────────────────┘
         │                 │                    │
         └─────────────────┼────────────────────┘
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Scraper Service (Flask)                           │
│                         Port: 5000                                   │
├─────────────────────────────────────────────────────────────────────┤
│  • Web scraping with BeautifulSoup                                  │
│  • Extracts: title, URL, full text                                  │
│  • 5 latest articles per source                                     │
│  • REST API endpoints:                                              │
│    - GET /scrape (all sources)                                      │
│    - GET /scrape/coindesk                                           │
│    - GET /scrape/cointelegraph                                      │
│    - GET /scrape/yahoo                                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Article Data (JSON)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Django Web Application                             │
│                         Port: 8080                                   │
├─────────────────────────────────────────────────────────────────────┤
│  • Main web interface and dashboard                                 │
│  • SQLite database for article storage                              │
│  • REST API endpoints:                                              │
│    - POST /api/scrape/ (trigger scraping)                           │
│    - POST /api/analyze/ (trigger analysis)                          │
│    - GET /api/articles/ (list articles)                             │
│    - GET /api/stats/ (sentiment statistics)                         │
│  • Admin panel at /admin                                            │
│  • Models: NewsArticle, SentimentAnalysis                           │
└────────┬──────────────────────────────────────────┬─────────────────┘
         │                                          │
         │ Analysis Request (JSON)                  │ Store Results
         ▼                                          │
┌─────────────────────────────────────────────────────────────────────┐
│              Sentiment Analysis Service (FastAPI)                    │
│                         Port: 8000                                   │
├─────────────────────────────────────────────────────────────────────┤
│  • LLM-based sentiment analysis                                     │
│  • Ollama Cloud integration                                         │
│  • REST API endpoints:                                              │
│    - POST /analyze (batch analysis)                                 │
│    - POST /analyze/single (single article)                          │
│    - GET /models (available LLM models)                             │
│  • Returns: sentiment, confidence, summary, key points              │
│  • Interactive API docs at /docs                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ LLM API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Ollama Cloud API                              │
│                  (External LLM Service)                              │
├─────────────────────────────────────────────────────────────────────┤
│  • Models: llama2, mistral, mixtral, neural-chat                    │
│  • Sentiment classification                                         │
│  • Text summarization                                               │
│  • Key point extraction                                             │
└─────────────────────────────────────────────────────────────────────┘


                         Data Flow Diagram
                         ─────────────────

User Request → Django Dashboard
       │
       ├─→ Click "Scrape Latest News"
       │     │
       │     └─→ Django → POST /api/scrape/
       │           │
       │           └─→ Scraper Service → GET /scrape
       │                 │
       │                 ├─→ Scrape CoinDesk
       │                 ├─→ Scrape CoinTelegraph
       │                 └─→ Scrape Yahoo Finance
       │                       │
       │                       └─→ Return Articles (JSON)
       │                             │
       │                             └─→ Django saves to database
       │
       ├─→ Click "Analyze Sentiment"
       │     │
       │     └─→ Django → POST /api/analyze/
       │           │
       │           └─→ Get unanalyzed articles from DB
       │                 │
       │                 └─→ Sentiment Service → POST /analyze
       │                       │
       │                       └─→ Ollama Cloud → LLM Analysis
       │                             │
       │                             └─→ Return Sentiment Results
       │                                   │
       │                                   └─→ Django updates DB
       │
       └─→ View Dashboard
             │
             └─→ Display:
                   • Total articles
                   • Sentiment distribution
                   • Market outlook
                   • Article list with sentiments


                    Deployment Architecture
                    ───────────────────────

Production (Docker Compose):

┌──────────────────────────────────────────────────────────────────┐
│                          Docker Network                           │
├──────────────┬────────────────┬────────────────┬─────────────────┤
│   Scraper    │   Sentiment    │    Django      │     Nginx       │
│  Container   │   Container    │   Container    │   Container     │
│  (Port 5000) │  (Port 8000)   │  (Port 8080)   │  (Port 80/443)  │
└──────────────┴────────────────┴────────────────┴─────────────────┘

Volumes:
  • db_volume: PostgreSQL/SQLite database
  • static_volume: Django static files
  • media_volume: Uploaded media files


                    Technology Stack
                    ────────────────

Backend Services:
  • Scraper: Flask + BeautifulSoup + Requests
  • Sentiment: FastAPI + Ollama Client + Pydantic
  • Web App: Django + SQLite/PostgreSQL

Frontend:
  • HTML5, CSS3, JavaScript (Vanilla)
  • Responsive design
  • AJAX for async operations

DevOps:
  • Docker & Docker Compose
  • Environment variable configuration
  • Health check endpoints

External Services:
  • Ollama Cloud for LLM inference
  • News sources (CoinDesk, CoinTelegraph, Yahoo Finance)


                    Security Measures
                    ─────────────────

✓ Flask debug mode disabled in production
✓ Django SECRET_KEY from environment variables
✓ CSRF protection on all POST endpoints
✓ Stack trace exposure prevented
✓ Input validation on all endpoints
✓ SQL injection prevention (Django ORM)
✓ XSS protection (Django templates)
✓ HTTPS support in production
✓ No hardcoded credentials


                    Scalability
                    ───────────

Horizontal Scaling:
  • Each service can be replicated independently
  • Load balancer distributes requests
  • Stateless design allows easy scaling

Vertical Scaling:
  • Resource limits configurable per service
  • Database can be migrated to PostgreSQL
  • Caching layer (Redis) can be added

Performance Optimizations:
  • Database indexes on frequently queried fields
  • Caching of sentiment results
  • Async task queues for background jobs
  • CDN for static assets


                    Monitoring
                    ──────────

Logging:
  • Service-level logging to stdout
  • Centralized log aggregation (optional)
  • Error tracking with Sentry (optional)

Metrics:
  • Health check endpoints
  • Response time monitoring
  • Error rate tracking
  • Resource usage monitoring

Alerts:
  • Service downtime
  • High error rates
  • Database connection issues
  • API rate limits
