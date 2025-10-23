"""
Web scraper service for collecting crypto news articles.
Scrapes latest 5 articles from CoinDesk, CoinTelegraph, and Yahoo Finance.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crypto-related keywords for filtering Yahoo Finance articles
CRYPTO_KEYWORDS = [
    'crypto', 'bitcoin', 'btc', 'ethereum', 'eth', 'blockchain',
    'defi', 'nft', 'coin', 'token', 'solana', 'cardano', 'polygon',
    'dogecoin', 'shiba', 'altcoin', 'web3', 'digital currency',
    'cryptocurrency', 'stablecoin', 'mining', 'wallet', 'exchange'
]


class CryptoNewsScraper:
    """Scraper for collecting crypto news from multiple sources."""
    
    def __init__(self):
        self.sources = {
            'coindesk': 'https://www.coindesk.com/',
            'cointelegraph': 'https://cointelegraph.com/',
            'yahoo_finance': 'https://finance.yahoo.com/topic/crypto/?guccounter=1'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_coindesk(self) -> List[Dict[str, str]]:
        """Scrape latest 5 articles from CoinDesk."""
        try:
            logger.info("Scraping CoinDesk...")
            response = requests.get(self.sources['coindesk'], headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            # Find article elements - CoinDesk uses multiple possible selectors
            # Try multiple selectors to be more robust
            article_elements = soup.find_all('a', class_='card-title-link', limit=10)
            
            # If the first selector doesn't work, try alternative selectors
            if not article_elements:
                article_elements = soup.find_all('a', class_=['card-title', 'articleTextLink'], limit=10)
            
            # Try finding article or div containers with links
            if not article_elements:
                containers = soup.find_all(['article', 'div'], class_=lambda x: x and ('card' in x.lower() or 'article' in x.lower()), limit=10)
                for container in containers:
                    link = container.find('a', href=True)
                    if link:
                        article_elements.append(link)
            
            for element in article_elements:
                title = element.get_text(strip=True)
                url = element.get('href', '')
                
                # Skip if title is too short
                if len(title) < 20:
                    continue
                
                if not url.startswith('http'):
                    url = 'https://www.coindesk.com' + url
                
                # Get article text
                article_text = self._get_article_text(url)
                
                articles.append({
                    'source': 'CoinDesk',
                    'title': title,
                    'url': url,
                    'text': article_text,
                    'scraped_at': datetime.now().isoformat()
                })
                
                # Stop once we have 5 articles
                if len(articles) >= 5:
                    break
            
            logger.info(f"Scraped {len(articles)} articles from CoinDesk")
            return articles
        except Exception as e:
            logger.error(f"Error scraping CoinDesk: {e}")
            return []
    
    def scrape_cointelegraph(self) -> List[Dict[str, str]]:
        """Scrape latest 5 articles from CoinTelegraph."""
        try:
            logger.info("Scraping CoinTelegraph...")
            response = requests.get(self.sources['cointelegraph'], headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            # Find article elements - CoinTelegraph uses specific structure
            # Try multiple selectors to be more robust
            article_elements = soup.find_all('article', class_='post-card-inline', limit=10)
            
            # If the first selector doesn't work, try alternatives
            if not article_elements:
                article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and ('post-card' in x.lower() or 'article' in x.lower()), limit=10)
            
            for element in article_elements:
                title_elem = element.find('a', class_='post-card-inline__title-link')
                
                # Try alternative selectors if the first one doesn't work
                if not title_elem:
                    title_elem = element.find('a', class_=lambda x: x and 'title' in x.lower())
                
                if not title_elem:
                    title_elem = element.find('a', href=True)
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    # Skip if title is too short
                    if len(title) < 20:
                        continue
                    
                    if not url.startswith('http'):
                        url = 'https://cointelegraph.com' + url
                    
                    # Get article text
                    article_text = self._get_article_text(url)
                    
                    articles.append({
                        'source': 'CoinTelegraph',
                        'title': title,
                        'url': url,
                        'text': article_text,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                    # Stop once we have 5 articles
                    if len(articles) >= 5:
                        break
            
            logger.info(f"Scraped {len(articles)} articles from CoinTelegraph")
            return articles
        except Exception as e:
            logger.error(f"Error scraping CoinTelegraph: {e}")
            return []
    
    def scrape_yahoo_finance(self) -> List[Dict[str, str]]:
        """Scrape latest 5 articles from Yahoo Finance Crypto."""
        try:
            logger.info("Scraping Yahoo Finance Crypto...")
            response = requests.get(self.sources['yahoo_finance'], headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            # Find article elements - Yahoo Finance crypto section uses specific structure
            # Look for h3 tags within article or list items that are within the crypto topic section
            article_containers = soup.find_all(['li', 'article'], limit=20)
            
            for container in article_containers:
                # Find h3 or h2 within the container
                heading = container.find(['h3', 'h2'])
                if not heading:
                    continue
                
                link_elem = heading.find('a')
                if link_elem:
                    title = link_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    
                    # Skip if title is too short or doesn't seem crypto-related
                    if len(title) < 20:
                        continue
                    
                    # Filter for crypto-related keywords in title or URL
                    title_lower = title.lower()
                    url_lower = url.lower()
                    is_crypto_related = any(keyword in title_lower or keyword in url_lower 
                                          for keyword in CRYPTO_KEYWORDS)
                    
                    if not is_crypto_related:
                        continue
                    
                    if url.startswith('/'):
                        url = 'https://finance.yahoo.com' + url
                    elif not url.startswith('http'):
                        continue
                    
                    # Get article text
                    article_text = self._get_article_text(url)
                    
                    articles.append({
                        'source': 'Yahoo Finance',
                        'title': title,
                        'url': url,
                        'text': article_text,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                    # Stop once we have 5 articles
                    if len(articles) >= 5:
                        break
            
            logger.info(f"Scraped {len(articles)} articles from Yahoo Finance")
            return articles
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance: {e}")
            return []
    
    def _get_article_text(self, url: str) -> str:
        """Extract article text from a given URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text from common article containers
            article_text = ""
            for tag in ['article', 'div[class*="article"]', 'div[class*="content"]']:
                content = soup.find(tag)
                if content:
                    article_text = content.get_text(separator=' ', strip=True)
                    break
            
            # If no specific article container found, get all paragraphs
            if not article_text:
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # Limit text length to avoid too large payloads
            return article_text[:5000] if article_text else "Article text not available"
        except Exception as e:
            logger.error(f"Error extracting article text from {url}: {e}")
            return "Article text not available"
    
    def scrape_all(self) -> List[Dict[str, str]]:
        """Scrape articles from all sources."""
        all_articles = []
        
        all_articles.extend(self.scrape_coindesk())
        all_articles.extend(self.scrape_cointelegraph())
        all_articles.extend(self.scrape_yahoo_finance())
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles


if __name__ == "__main__":
    scraper = CryptoNewsScraper()
    articles = scraper.scrape_all()
    
    for article in articles:
        print(f"\n{'='*80}")
        print(f"Source: {article['source']}")
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Text preview: {article['text'][:200]}...")
        print(f"Scraped at: {article['scraped_at']}")
