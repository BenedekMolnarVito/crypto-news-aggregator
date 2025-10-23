#!/usr/bin/env python3
"""
Integration test script for crypto news aggregator.
Demonstrates the flow: scrape -> analyze -> view results
"""

import requests
import time
import json
from typing import Dict, List


class CryptoNewsAggregatorTest:
    """Test the complete flow of the crypto news aggregator."""
    
    def __init__(self):
        self.scraper_url = "http://localhost:5000"
        self.sentiment_url = "http://localhost:8000"
        self.webapp_url = "http://localhost:8080"
    
    def check_services(self) -> Dict[str, bool]:
        """Check if all services are running."""
        print("\n🔍 Checking service health...")
        
        services = {
            'scraper': False,
            'sentiment': False,
            'webapp': False
        }
        
        try:
            response = requests.get(f"{self.scraper_url}/health", timeout=5)
            services['scraper'] = response.status_code == 200
            print(f"  ✅ Scraper service: {'OK' if services['scraper'] else 'FAILED'}")
        except Exception as e:
            print(f"  ❌ Scraper service: FAILED ({e})")
        
        try:
            response = requests.get(f"{self.sentiment_url}/health", timeout=5)
            services['sentiment'] = response.status_code == 200
            print(f"  ✅ Sentiment service: {'OK' if services['sentiment'] else 'FAILED'}")
        except Exception as e:
            print(f"  ❌ Sentiment service: FAILED ({e})")
        
        try:
            response = requests.get(f"{self.webapp_url}/api/stats/", timeout=5)
            services['webapp'] = response.status_code == 200
            print(f"  ✅ Web app: {'OK' if services['webapp'] else 'FAILED'}")
        except Exception as e:
            print(f"  ❌ Web app: FAILED ({e})")
        
        return services
    
    def test_scraper(self) -> List[Dict]:
        """Test the scraper service."""
        print("\n📰 Testing scraper service...")
        
        try:
            # Note: In restricted environments, this may return empty results
            response = requests.get(f"{self.scraper_url}/scrape", timeout=30)
            data = response.json()
            
            if data['success']:
                print(f"  ✅ Scraped {data['count']} articles")
                return data.get('articles', [])
            else:
                print(f"  ⚠️  Scraping returned no articles (may be network restricted)")
                return []
        except Exception as e:
            print(f"  ❌ Scraper test failed: {e}")
            return []
    
    def test_sentiment_analysis(self, articles: List[Dict] = None) -> Dict:
        """Test the sentiment analysis service."""
        print("\n🧠 Testing sentiment analysis service...")
        
        # Use sample data if no articles provided
        if not articles:
            articles = [
                {
                    "title": "Bitcoin Reaches New All-Time High",
                    "text": "Bitcoin (BTC) has surged to a new all-time high today, reaching $75,000 per coin. Market analysts attribute the rally to increased institutional adoption and positive regulatory developments. Trading volumes have spiked 300% over the past week.",
                    "source": "Sample",
                    "url": "https://example.com/btc-ath"
                },
                {
                    "title": "Ethereum Network Faces Scalability Concerns",
                    "text": "The Ethereum network is experiencing congestion issues as transaction fees spike to record highs. Users report delays in transaction confirmations. Developers are working on Layer 2 solutions to address the scalability problems.",
                    "source": "Sample",
                    "url": "https://example.com/eth-scalability"
                },
                {
                    "title": "Cryptocurrency Adoption Growing in Emerging Markets",
                    "text": "New data shows cryptocurrency adoption is accelerating in emerging markets, particularly in Latin America and Southeast Asia. The trend is driven by remittance use cases and inflation hedging strategies.",
                    "source": "Sample",
                    "url": "https://example.com/crypto-adoption"
                }
            ]
            print("  ℹ️  Using sample articles for testing")
        
        try:
            response = requests.post(
                f"{self.sentiment_url}/analyze",
                json={"articles": articles[:3]},  # Limit to 3 articles for testing
                timeout=60
            )
            data = response.json()
            
            if data.get('success'):
                print(f"  ✅ Analyzed {len(data.get('results', []))} articles")
                print(f"  📊 Overall sentiment: {data.get('overall_sentiment', 'N/A')}")
                print(f"  📈 Market outlook: {data.get('market_outlook', 'N/A')[:80]}...")
                
                # Display individual results
                for result in data.get('results', []):
                    sentiment_emoji = {
                        'positive': '😊',
                        'negative': '😟',
                        'neutral': '😐'
                    }.get(result['sentiment'], '❓')
                    
                    print(f"\n  {sentiment_emoji} {result['title'][:60]}...")
                    print(f"     Sentiment: {result['sentiment']} (confidence: {result['confidence']:.2f})")
                    print(f"     Summary: {result['summary'][:100]}...")
                
                return data
            else:
                print(f"  ❌ Analysis failed")
                return {}
        except Exception as e:
            print(f"  ❌ Sentiment analysis test failed: {e}")
            return {}
    
    def test_webapp_stats(self):
        """Test the web app statistics endpoint."""
        print("\n📊 Testing web app statistics...")
        
        try:
            response = requests.get(f"{self.webapp_url}/api/stats/", timeout=5)
            data = response.json()
            
            print(f"  ✅ Total articles in database: {data.get('total_articles', 0)}")
            
            dist = data.get('sentiment_distribution', {})
            print(f"     Positive: {dist.get('positive', 0)}")
            print(f"     Negative: {dist.get('negative', 0)}")
            print(f"     Neutral: {dist.get('neutral', 0)}")
            
            return data
        except Exception as e:
            print(f"  ❌ Web app stats test failed: {e}")
            return {}
    
    def run_full_test(self):
        """Run the complete integration test."""
        print("=" * 70)
        print("🚀 Crypto News Aggregator Integration Test")
        print("=" * 70)
        
        # Check services
        services = self.check_services()
        
        if not all(services.values()):
            print("\n⚠️  Warning: Not all services are running!")
            print("   Please ensure all services are started before running tests.")
            return
        
        # Test scraper
        articles = self.test_scraper()
        
        # Test sentiment analysis
        sentiment_results = self.test_sentiment_analysis(articles)
        
        # Test web app stats
        stats = self.test_webapp_stats()
        
        print("\n" + "=" * 70)
        print("✅ Integration test completed!")
        print("=" * 70)
        print("\n📱 Access the dashboard at: http://localhost:8080")
        print("📚 API documentation at: http://localhost:8000/docs")
        print("\n")


if __name__ == "__main__":
    tester = CryptoNewsAggregatorTest()
    tester.run_full_test()
