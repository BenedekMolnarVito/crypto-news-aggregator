"""
Flask API for the web scraper service.
Provides endpoints to trigger scraping and retrieve articles.
"""

from flask import Flask, jsonify
from scraper import CryptoNewsScraper
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
scraper = CryptoNewsScraper()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'scraper'}), 200


@app.route('/scrape', methods=['GET'])
def scrape_news():
    """Scrape news from all sources."""
    try:
        articles = scraper.scrape_all()
        return jsonify({
            'success': True,
            'count': len(articles),
            'articles': articles
        }), 200
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to scrape articles'
        }), 500


@app.route('/scrape/coindesk', methods=['GET'])
def scrape_coindesk():
    """Scrape news from CoinDesk only."""
    try:
        articles = scraper.scrape_coindesk()
        return jsonify({
            'success': True,
            'count': len(articles),
            'articles': articles
        }), 200
    except Exception as e:
        logger.error(f"Error in coindesk endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to scrape CoinDesk'
        }), 500


@app.route('/scrape/cointelegraph', methods=['GET'])
def scrape_cointelegraph():
    """Scrape news from CoinTelegraph only."""
    try:
        articles = scraper.scrape_cointelegraph()
        return jsonify({
            'success': True,
            'count': len(articles),
            'articles': articles
        }), 200
    except Exception as e:
        logger.error(f"Error in cointelegraph endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to scrape CoinTelegraph'
        }), 500


@app.route('/scrape/yahoo', methods=['GET'])
def scrape_yahoo():
    """Scrape news from Yahoo Finance only."""
    try:
        articles = scraper.scrape_yahoo_finance()
        return jsonify({
            'success': True,
            'count': len(articles),
            'articles': articles
        }), 200
    except Exception as e:
        logger.error(f"Error in yahoo endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to scrape Yahoo Finance'
        }), 500


if __name__ == '__main__':
    import sys
    
    # Check if we should enable debug mode
    debug_mode = "--debug" in sys.argv or os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', '5000'))
    
    if debug_mode:
        logger.info("Starting Flask in DEBUG mode...")
        # Enable auto-reload for development
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=True,
            use_reloader=True,
            use_debugger=True
        )
    else:
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
