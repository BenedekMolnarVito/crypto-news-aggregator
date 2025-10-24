from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.urls import reverse_lazy
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


class LoginView(View):
    """Login view."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('news:home')
        return render(request, 'news/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'news:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'news/login.html')


class LogoutView(View):
    """Logout view."""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully')
        return redirect('news:login')
    
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully')
        return redirect('news:login')


class SignupView(View):
    """Signup view."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('news:home')
        return render(request, 'news/signup.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if not username or not email or not password1 or not password2:
            messages.error(request, 'All fields are required')
            return render(request, 'news/signup.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'news/signup.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'news/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'news/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'news/signup.html')
        
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('news:home')
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            messages.error(request, 'Error creating account. Please try again.')
            return render(request, 'news/signup.html')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view."""
    template_name = 'news/password_reset.html'
    email_template_name = 'news/password_reset_email.html'
    subject_template_name = 'news/password_reset_subject.txt'
    success_url = reverse_lazy('news:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Password reset done view."""
    template_name = 'news/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirm view."""
    template_name = 'news/password_reset_confirm.html'
    success_url = reverse_lazy('news:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset complete view."""
    template_name = 'news/password_reset_complete.html'


class HomeView(LoginRequiredMixin, View):
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
            
            articles_to_analyze = NewsArticle.objects.filter(scraped_at__date=timezone.now().date())

            if not articles_to_analyze:
                return Response({
                    'success': True,
                    'message': 'No articles to analyze'
                })

            # Analyze articles
            results = sentiment_service.analyze_articles(list(articles_to_analyze))
            
            return Response({
                'success': True,
                'message': f'Analyzed {len(results)} articles',
                'count': len(results)
            })
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}", exc_info=True)
            # Don't expose detailed error messages to users for security
            return JsonResponse({
                'success': False,
                'error': 'Failed to analyze sentiment. Please try again or contact support.'
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


class ClearArticlesView(APIView):
    """API view to clear all articles from the database."""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Delete all articles and sentiment analysis data from the database",
        tags=['Articles Management'],
        responses={
            200: openapi.Response('Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'deleted_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        try:
            # Count articles before deletion
            article_count = NewsArticle.objects.count()
            sentiment_count = SentimentAnalysis.objects.count()
            
            # Delete all articles and sentiment analysis
            NewsArticle.objects.all().delete()
            SentimentAnalysis.objects.all().delete()
            
            logger.info(f"Cleared {article_count} articles and {sentiment_count} sentiment analyses")
            
            return Response({
                'success': True,
                'message': f'Successfully cleared {article_count} articles',
                'deleted_count': article_count
            })
        except Exception as e:
            logger.error(f"Error clearing articles: {e}")
            return Response({
                'success': False,
                'error': 'Failed to clear articles'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


