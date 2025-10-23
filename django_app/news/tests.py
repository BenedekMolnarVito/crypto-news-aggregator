from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import patch, Mock
from .models import NewsArticle, SentimentAnalysis
from .services import ScraperService, SentimentService
import json


class NewsArticleModelTest(TestCase):
    """Test cases for NewsArticle model."""
    
    def setUp(self):
        """Set up test data."""
        self.article = NewsArticle.objects.create(
            title="Bitcoin Reaches New High",
            url="https://example.com/bitcoin-high",
            source="coindesk",
            text="Bitcoin has reached a new all-time high today.",
            sentiment="positive",
            confidence=0.85,
            summary="Bitcoin bullish momentum continues"
        )
    
    def test_article_creation(self):
        """Test article is created correctly."""
        self.assertEqual(self.article.title, "Bitcoin Reaches New High")
        self.assertEqual(self.article.source, "coindesk")
        self.assertEqual(self.article.sentiment, "positive")
        self.assertIsNotNone(self.article.scraped_at)
    
    def test_article_str_representation(self):
        """Test string representation of article."""
        expected = f"coindesk: {self.article.title[:50]}"
        self.assertEqual(str(self.article), expected)
    
    def test_article_url_unique(self):
        """Test that article URL must be unique."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            NewsArticle.objects.create(
                title="Duplicate Article",
                url="https://example.com/bitcoin-high",  # Same URL
                source="cointelegraph",
                text="Different content"
            )
    
    def test_article_ordering(self):
        """Test articles are ordered by scraped_at descending."""
        article2 = NewsArticle.objects.create(
            title="Ethereum Update",
            url="https://example.com/eth-update",
            source="cointelegraph",
            text="Ethereum network upgrade successful"
        )
        articles = NewsArticle.objects.all()
        self.assertEqual(articles[0], article2)  # Most recent first
        self.assertEqual(articles[1], self.article)
    
    def test_sentiment_choices(self):
        """Test sentiment field accepts valid choices."""
        for sentiment, _ in NewsArticle.SENTIMENT_CHOICES:
            article = NewsArticle.objects.create(
                title=f"Test {sentiment}",
                url=f"https://example.com/test-{sentiment}",
                source="coindesk",
                text="Test content",
                sentiment=sentiment
            )
            self.assertEqual(article.sentiment, sentiment)


class SentimentAnalysisModelTest(TestCase):
    """Test cases for SentimentAnalysis model."""
    
    def setUp(self):
        """Set up test data."""
        self.analysis = SentimentAnalysis.objects.create(
            date=date.today(),
            overall_sentiment="bullish",
            positive_count=15,
            negative_count=5,
            neutral_count=3,
            market_outlook="Market is trending positive",
            articles_analyzed=23
        )
    
    def test_analysis_creation(self):
        """Test sentiment analysis is created correctly."""
        self.assertEqual(self.analysis.overall_sentiment, "bullish")
        self.assertEqual(self.analysis.articles_analyzed, 23)
        self.assertEqual(self.analysis.positive_count, 15)
    
    def test_analysis_str_representation(self):
        """Test string representation."""
        expected = f"Sentiment Analysis - {self.analysis.date}"
        self.assertEqual(str(self.analysis), expected)
    
    def test_analysis_date_unique(self):
        """Test that date must be unique."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            SentimentAnalysis.objects.create(
                date=date.today(),
                overall_sentiment="bearish",
                positive_count=5,
                negative_count=10,
                neutral_count=2,
                market_outlook="Different outlook",
                articles_analyzed=17
            )
    
    def test_analysis_ordering(self):
        """Test analyses are ordered by date descending."""
        yesterday_analysis = SentimentAnalysis.objects.create(
            date=date.today() - timedelta(days=1),
            overall_sentiment="neutral",
            positive_count=10,
            negative_count=10,
            neutral_count=5,
            market_outlook="Mixed signals",
            articles_analyzed=25
        )
        analyses = SentimentAnalysis.objects.all()
        self.assertEqual(analyses[0], self.analysis)  # Most recent first


class HomeViewTest(TestCase):
    """Test cases for HomeView."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.url = reverse('news:home')
        
        # Create test articles
        for i in range(5):
            NewsArticle.objects.create(
                title=f"Article {i}",
                url=f"https://example.com/article-{i}",
                source="coindesk",
                text=f"Content {i}",
                sentiment="positive" if i % 2 == 0 else "negative"
            )
        
        # Create sentiment analysis
        SentimentAnalysis.objects.create(
            date=date.today(),
            overall_sentiment="bullish",
            positive_count=3,
            negative_count=2,
            neutral_count=0,
            market_outlook="Positive trend",
            articles_analyzed=5
        )
    
    def test_home_view_status_code(self):
        """Test home view returns 200 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_home_view_uses_correct_template(self):
        """Test home view uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'news/dashboard.html')
    
    def test_home_view_context_data(self):
        """Test home view provides correct context."""
        response = self.client.get(self.url)
        self.assertIn('articles', response.context)
        self.assertIn('latest_analysis', response.context)
        self.assertIn('total_articles', response.context)
        self.assertEqual(response.context['total_articles'], 5)
        self.assertEqual(response.context['positive_count'], 3)
        self.assertEqual(response.context['negative_count'], 2)


class ScrapeNewsViewTest(TestCase):
    """Test cases for ScrapeNewsView."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('news:scrape')
    
    @patch('news.views.ScraperService')
    def test_scrape_news_success(self, mock_scraper):
        """Test successful news scraping."""
        mock_instance = Mock()
        mock_instance.scrape_and_save.return_value = [
            {'title': 'Test Article', 'url': 'https://example.com/test'}
        ]
        mock_scraper.return_value = mock_instance
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
    
    @patch('news.views.ScraperService')
    def test_scrape_news_failure(self, mock_scraper):
        """Test news scraping failure."""
        mock_instance = Mock()
        mock_instance.scrape_and_save.side_effect = Exception("Scraping failed")
        mock_scraper.return_value = mock_instance
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 500)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)


class AnalyzeSentimentViewTest(TestCase):
    """Test cases for AnalyzeSentimentView."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.url = reverse('news:analyze')
        
        # Create unanalyzed articles
        for i in range(3):
            NewsArticle.objects.create(
                title=f"Unanalyzed Article {i}",
                url=f"https://example.com/unanalyzed-{i}",
                source="coindesk",
                text=f"Content {i}"
            )
    
    @patch('news.views.SentimentService')
    def test_analyze_sentiment_success(self, mock_service):
        """Test successful sentiment analysis."""
        mock_instance = Mock()
        mock_instance.analyze_articles.return_value = [
            {'title': 'Article 1', 'sentiment': 'positive'}
        ]
        mock_service.return_value = mock_instance
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_analyze_no_articles(self):
        """Test analysis when no unanalyzed articles exist."""
        # Analyze all existing articles
        NewsArticle.objects.all().update(sentiment='positive')
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('No articles to analyze', data['message'])


class ArticleListViewTest(TestCase):
    """Test cases for ArticleListView."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.url = reverse('news:articles')
        
        for i in range(10):
            NewsArticle.objects.create(
                title=f"Article {i}",
                url=f"https://example.com/article-{i}",
                source="coindesk",
                text=f"Content {i}",
                sentiment="positive"
            )
    
    def test_article_list_view(self):
        """Test article list API returns correct data."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('articles', data)
        self.assertEqual(len(data['articles']), 10)


class SentimentStatsViewTest(TestCase):
    """Test cases for SentimentStatsView."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.url = reverse('news:stats')
        
        NewsArticle.objects.create(
            title="Positive Article",
            url="https://example.com/positive",
            source="coindesk",
            text="Content",
            sentiment="positive"
        )
        NewsArticle.objects.create(
            title="Negative Article",
            url="https://example.com/negative",
            source="cointelegraph",
            text="Content",
            sentiment="negative"
        )
        
        SentimentAnalysis.objects.create(
            date=date.today(),
            overall_sentiment="neutral",
            positive_count=1,
            negative_count=1,
            neutral_count=0,
            market_outlook="Mixed market",
            articles_analyzed=2
        )
    
    def test_sentiment_stats_view(self):
        """Test sentiment stats API returns correct data."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['total_articles'], 2)
        self.assertEqual(data['sentiment_distribution']['positive'], 1)
        self.assertEqual(data['sentiment_distribution']['negative'], 1)
        self.assertIsNotNone(data['latest_analysis'])


class ScraperServiceTest(TestCase):
    """Test cases for ScraperService."""
    
    @patch('news.services.requests.get')
    def test_scraper_service_initialization(self, mock_get):
        """Test ScraperService initializes correctly."""
        service = ScraperService()
        self.assertIsNotNone(service.scraper_url)
    
    @patch('news.services.requests.get')
    def test_scrape_and_save_success(self, mock_get):
        """Test successful scraping and saving."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'articles': [
                {
                    'title': 'Test Article',
                    'url': 'https://example.com/test',
                    'source': 'CoinDesk',
                    'text': 'Test content',
                    'scraped_at': timezone.now().isoformat()
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ScraperService()
        articles = service.scrape_and_save()
        
        self.assertEqual(len(articles), 1)
        self.assertEqual(NewsArticle.objects.count(), 1)
        
        saved_article = NewsArticle.objects.first()
        self.assertEqual(saved_article.title, 'Test Article')


class SentimentServiceTest(TestCase):
    """Test cases for SentimentService."""
    
    def setUp(self):
        """Set up test data."""
        self.article = NewsArticle.objects.create(
            title="Test Article",
            url="https://example.com/test",
            source="coindesk",
            text="Bitcoin is performing well in the market"
        )
    
    @patch('news.services.requests.post')
    def test_sentiment_service_analyze(self, mock_post):
        """Test sentiment analysis service."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'results': [
                {
                    'title': 'Test Article',
                    'sentiment': 'positive',
                    'confidence': 0.85,
                    'summary': 'Positive market outlook',
                    'key_points': ['Bitcoin performing well']
                }
            ],
            'overall_sentiment': 'bullish',
            'market_outlook': 'Market trending positive'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        service = SentimentService()
        results = service.analyze_articles([self.article])
        
        self.assertEqual(len(results), 1)
        
        # Refresh article from database
        self.article.refresh_from_db()
        self.assertEqual(self.article.sentiment, 'positive')
        self.assertEqual(self.article.confidence, 0.85)
        self.assertIsNotNone(self.article.analyzed_at)

