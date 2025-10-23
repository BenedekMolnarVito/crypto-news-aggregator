from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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


class ScrapeNewsView(APIView):
    """API view to trigger news scraping."""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Trigger news scraping from various crypto sources",
        tags=['News Scraping'],
        responses={
            200: openapi.Response('Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        try:
            scraper_service = ScraperService()
            articles = scraper_service.scrape_and_save()
            
            return Response({
                'success': True,
                'message': f'Successfully scraped {len(articles)} articles',
                'count': len(articles)
            })
        except Exception as e:
            logger.error(f"Error scraping news: {e}")
            return Response({
                'success': False,
                'error': 'Failed to scrape news articles'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalyzeSentimentView(APIView):
    """API view to trigger sentiment analysis."""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Analyze sentiment of unanalyzed articles",
        responses={
            200: openapi.Response('Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        try:
            sentiment_service = SentimentService()
            
            # Get unanalyzed articles
            unanalyzed_articles = NewsArticle.objects.filter(sentiment__isnull=True)[:10]
            
            if not unanalyzed_articles:
                return Response({
                    'success': True,
                    'message': 'No articles to analyze'
                })
            
            # Analyze articles
            results = sentiment_service.analyze_articles(list(unanalyzed_articles))
            
            return Response({
                'success': True,
                'message': f'Analyzed {len(results)} articles',
                'count': len(results)
            })
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return Response({
                'success': False,
                'error': 'Failed to analyze sentiment'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleListView(APIView):
    """API view to list articles."""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get list of latest articles",
        responses={
            200: openapi.Response('Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'articles': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'title': openapi.Schema(type=openapi.TYPE_STRING),
                                'source': openapi.Schema(type=openapi.TYPE_STRING),
                                'url': openapi.Schema(type=openapi.TYPE_STRING),
                                'sentiment': openapi.Schema(type=openapi.TYPE_STRING),
                                'confidence': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'scraped_at': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    )
                }
            ))
        }
    )
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
        
        return Response({'articles': data})


class SentimentStatsView(APIView):
    """API view for sentiment statistics."""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get sentiment statistics and analysis",
        responses={
            200: openapi.Response('Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_articles': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'sentiment_distribution': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'positive': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'negative': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'neutral': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    ),
                    'latest_analysis': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'date': openapi.Schema(type=openapi.TYPE_STRING),
                            'overall_sentiment': openapi.Schema(type=openapi.TYPE_STRING),
                            'market_outlook': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            ))
        }
    )
    def get(self, request):
        # Overall stats
        total = NewsArticle.objects.count()
        positive = NewsArticle.objects.filter(sentiment='positive').count()
        negative = NewsArticle.objects.filter(sentiment='negative').count()
        neutral = NewsArticle.objects.filter(sentiment='neutral').count()
        
        # Recent analysis
        recent_analysis = SentimentAnalysis.objects.first()
        
        return Response({
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

