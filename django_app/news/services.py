"""
Services for interacting with scraper and sentiment analysis microservices.
"""

import requests
from django.conf import settings
from django.utils import timezone
from .models import NewsArticle, SentimentAnalysis
from datetime import date
import logging

logger = logging.getLogger(__name__)


class ScraperService:
    """Service to interact with the scraper microservice."""
    
    def __init__(self):
        self.scraper_url = getattr(settings, 'SCRAPER_SERVICE_URL', 'http://localhost:5000')
    
    def scrape_and_save(self):
        """Scrape news articles and save to database."""
        try:
            response = requests.get(f'{self.scraper_url}/scrape', timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            saved_articles = []
            for article_data in articles:
                # Check if article already exists
                if not NewsArticle.objects.filter(url=article_data['url']).exists():
                    article = NewsArticle.objects.create(
                        title=article_data['title'],
                        url=article_data['url'],
                        source=self._normalize_source(article_data['source']),
                        text=article_data['text'],
                        scraped_at=timezone.now()
                    )
                    saved_articles.append(article)
                    logger.info(f"Saved article: {article.title}")
            
            return saved_articles
        
        except requests.RequestException as e:
            logger.error(f"Error calling scraper service: {e}")
            raise
    
    def _normalize_source(self, source: str) -> str:
        """Normalize source name to match model choices."""
        source_lower = source.lower()
        if 'coindesk' in source_lower:
            return 'coindesk'
        elif 'cointelegraph' in source_lower:
            return 'cointelegraph'
        elif 'yahoo' in source_lower:
            return 'yahoo_finance'
        return 'coindesk'  # default


class SentimentService:
    """Service to interact with the sentiment analysis microservice."""
    
    def __init__(self):
        self.sentiment_url = getattr(settings, 'SENTIMENT_SERVICE_URL', 'http://localhost:8000')
    
    def analyze_articles(self, articles):
        """Analyze sentiment of articles using the FastAPI service."""
        try:
            # Prepare articles data
            articles_data = [{
                'title': article.title,
                'text': article.text,
                'source': article.source,
                'url': article.url
            } for article in articles]
            
            # Call sentiment analysis service
            response = requests.post(
                f'{self.sentiment_url}/analyze',
                json={'articles': articles_data},
                timeout=60
            )
            
            # Check if response is successful
            if response.status_code != 200:
                logger.error(f"Sentiment service returned status {response.status_code}: {response.text}")
                raise Exception(f"Sentiment service error: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            # Update articles with sentiment data
            for i, result in enumerate(results):
                if i < len(articles):
                    article = articles[i]
                    article.sentiment = result['sentiment']
                    article.confidence = result['confidence']
                    article.summary = result['summary']
                    article.analyzed_at = timezone.now()
                    article.save()
                    logger.info(f"Updated sentiment for: {article.title}")
            
            # Save overall sentiment analysis
            self._save_sentiment_analysis(data)
            
            return results
        
        except requests.ConnectionError as e:
            logger.error(f"Cannot connect to sentiment service at {self.sentiment_url}: {e}")
            raise Exception(f"Cannot connect to sentiment analysis service. Please ensure it is running at {self.sentiment_url}")
        except requests.Timeout as e:
            logger.error(f"Sentiment service timeout: {e}")
            raise Exception("Sentiment analysis service timed out. Please try again.")
        except requests.RequestException as e:
            logger.error(f"Error calling sentiment service: {e}")
            raise Exception(f"Error communicating with sentiment service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in sentiment analysis: {e}")
            raise
    
    def _save_sentiment_analysis(self, data):
        """Save aggregated sentiment analysis."""
        today = date.today()
        
        # Count sentiments
        positive = sum(1 for r in data['results'] if r['sentiment'] == 'positive')
        negative = sum(1 for r in data['results'] if r['sentiment'] == 'negative')
        neutral = sum(1 for r in data['results'] if r['sentiment'] == 'neutral')
        
        SentimentAnalysis.objects.update_or_create(
            date=today,
            defaults={
                'overall_sentiment': data.get('overall_sentiment', 'neutral'),
                'positive_count': positive,
                'negative_count': negative,
                'neutral_count': neutral,
                'market_outlook': data.get('market_outlook', ''),
                'articles_analyzed': len(data['results'])
            }
        )
