from django.contrib import admin
from .models import NewsArticle, SentimentAnalysis


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'sentiment', 'confidence', 'scraped_at')
    list_filter = ('source', 'sentiment', 'scraped_at')
    search_fields = ('title', 'text')
    readonly_fields = ('scraped_at', 'analyzed_at', 'created_at', 'updated_at')
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'url', 'source', 'text', 'scraped_at')
        }),
        ('Sentiment Analysis', {
            'fields': ('sentiment', 'confidence', 'summary', 'analyzed_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('date', 'overall_sentiment', 'articles_analyzed', 'positive_count', 'negative_count', 'neutral_count')
    list_filter = ('overall_sentiment', 'date')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Analysis Date', {
            'fields': ('date',)
        }),
        ('Sentiment Breakdown', {
            'fields': ('overall_sentiment', 'market_outlook', 'articles_analyzed')
        }),
        ('Distribution', {
            'fields': ('positive_count', 'negative_count', 'neutral_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

