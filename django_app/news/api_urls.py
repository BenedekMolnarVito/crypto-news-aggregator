"""
API URL configuration for news app using DRF router.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for viewsets (though we're using APIView, we'll use paths)
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('scrape/', views.ScrapeNewsView.as_view(), name='api-scrape'),
    path('analyze/', views.AnalyzeSentimentView.as_view(), name='api-analyze'), 
    path('articles/', views.ArticleListView.as_view(), name='api-articles'),
    path('stats/', views.SentimentStatsView.as_view(), name='api-stats'),
]