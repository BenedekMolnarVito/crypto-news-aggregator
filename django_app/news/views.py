from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from .models import NewsArticle, SentimentAnalysis
from .services import ScraperService, SentimentService
import logging

logger = logging.getLogger(__name__)


class HomeView(View):
    """Main dashboard view."""
    
    def get(self, request):
        # Get latest articles
        latest_articles = NewsArticle.objects.all()[:20]
        
        # Get latest sentiment analysis
        latest_analysis = SentimentAnalysis.objects.first()
        
        # Calculate sentiment distribution
        total_articles = NewsArticle.objects.count()
        positive_count = NewsArticle.objects.filter(sentiment='positive').count()
        negative_count = NewsArticle.objects.filter(sentiment='negative').count()
        neutral_count = NewsArticle.objects.filter(sentiment='neutral').count()
        
        context = {
            'articles': latest_articles,
            'latest_analysis': latest_analysis,
            'total_articles': total_articles,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
        }
        
        return render(request, 'news/dashboard.html', context)


class ScrapeNewsView(View):
    """View to trigger news scraping."""
    
    def post(self, request):
        try:
            scraper_service = ScraperService()
            articles = scraper_service.scrape_and_save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully scraped {len(articles)} articles',
                'count': len(articles)
            })
        except Exception as e:
            logger.error(f"Error scraping news: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to scrape news articles'
            }, status=500)


class AnalyzeSentimentView(View):
    """View to trigger sentiment analysis."""
    
    def post(self, request):
        try:
            sentiment_service = SentimentService()
            
            # Get unanalyzed articles
            unanalyzed_articles = NewsArticle.objects.filter(sentiment__isnull=True)[:10]
            
            if not unanalyzed_articles:
                return JsonResponse({
                    'success': True,
                    'message': 'No articles to analyze'
                })
            
            # Analyze articles
            results = sentiment_service.analyze_articles(list(unanalyzed_articles))
            
            return JsonResponse({
                'success': True,
                'message': f'Analyzed {len(results)} articles',
                'count': len(results)
            })
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to analyze sentiment'
            }, status=500)


class ArticleListView(View):
    """API view to list articles."""
    
    def get(self, request):
        articles = NewsArticle.objects.all()[:50]
        
        data = [{
            'id': article.id,
            'title': article.title,
            'source': article.source,
            'url': article.url,
            'sentiment': article.sentiment,
            'confidence': article.confidence,
            'scraped_at': article.scraped_at.isoformat(),
        } for article in articles]
        
        return JsonResponse({'articles': data})


class SentimentStatsView(View):
    """API view for sentiment statistics."""
    
    def get(self, request):
        # Overall stats
        total = NewsArticle.objects.count()
        positive = NewsArticle.objects.filter(sentiment='positive').count()
        negative = NewsArticle.objects.filter(sentiment='negative').count()
        neutral = NewsArticle.objects.filter(sentiment='neutral').count()
        
        # Recent analysis
        recent_analysis = SentimentAnalysis.objects.first()
        
        return JsonResponse({
            'total_articles': total,
            'sentiment_distribution': {
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
            },
            'latest_analysis': {
                'date': recent_analysis.date.isoformat() if recent_analysis else None,
                'overall_sentiment': recent_analysis.overall_sentiment if recent_analysis else None,
                'market_outlook': recent_analysis.market_outlook if recent_analysis else None,
            } if recent_analysis else None
        })

