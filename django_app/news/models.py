from django.db import models
from django.utils import timezone


class NewsArticle(models.Model):
    """Model for storing scraped news articles."""
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    
    SOURCE_CHOICES = [
        ('coindesk', 'CoinDesk'),
        ('cointelegraph', 'CoinTelegraph'),
        ('yahoo_finance', 'Yahoo Finance'),
    ]
    
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    text = models.TextField()
    scraped_at = models.DateTimeField(default=timezone.now)
    
    # Sentiment analysis fields
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['-scraped_at']),
            models.Index(fields=['sentiment']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.source}: {self.title[:50]}"


class SentimentAnalysis(models.Model):
    """Model for storing aggregated sentiment analysis."""
    
    date = models.DateField(unique=True)
    overall_sentiment = models.CharField(max_length=20)
    positive_count = models.IntegerField(default=0)
    negative_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)
    market_outlook = models.TextField()
    articles_analyzed = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Sentiment Analyses"
    
    def __str__(self):
        return f"Sentiment Analysis - {self.date}"
