"""
URL configuration for news app.
"""

from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('api/scrape/', views.ScrapeNewsView.as_view(), name='scrape'),
    path('api/analyze/', views.AnalyzeSentimentView.as_view(), name='analyze'),
    path('api/articles/', views.ArticleListView.as_view(), name='articles'),
    path('api/stats/', views.SentimentStatsView.as_view(), name='stats'),
]
