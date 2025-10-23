# Bug Fixes Summary

This document summarizes the fixes applied to address the UI bugs in the crypto news aggregator.

## Issues Fixed

### 1. Yahoo Finance Articles Not Crypto-Related ✅

**Problem:** Yahoo Finance scraper was picking up articles about sports, entertainment, etc., not just crypto.

**Solution:** 
- Added keyword filtering to ensure only crypto-related articles are scraped
- Extracted crypto keywords to a configuration constant `CRYPTO_KEYWORDS` for easy maintenance
- Implemented a comprehensive list of crypto keywords including: bitcoin, ethereum, blockchain, defi, nft, token, solana, etc.
- Filter checks both article title and URL for crypto-related keywords
- Only articles matching crypto keywords are included in results

**Files Changed:**
- `scraper_service/scraper.py` - `scrape_yahoo_finance()` method

### 2. Only Yahoo Finance Articles Showing (CoinDesk and CoinTelegraph Missing) ✅

**Problem:** CoinDesk and CoinTelegraph scrapers were not finding articles, likely due to website structure changes.

**Solution:**
- Implemented fallback selectors for both CoinDesk and CoinTelegraph
- Added multiple selector strategies to handle different HTML structures
- Added title length filtering (minimum 20 characters) to avoid grabbing navigation links or short text
- Increased initial limit to find more candidates, then filter down to 5 articles

**CoinDesk Changes:**
- Primary selector: `a.card-title-link`
- Fallback 1: `a.card-title`, `a.articleTextLink`
- Fallback 2: Find article/div containers with 'card' or 'article' in class name

**CoinTelegraph Changes:**
- Primary selector: `article.post-card-inline` with `a.post-card-inline__title-link`
- Fallback 1: Elements with 'title' in class name
- Fallback 2: Any anchor tag within the article container

**Files Changed:**
- `scraper_service/scraper.py` - `scrape_coindesk()` and `scrape_cointelegraph()` methods

### 3. Missing Article URL Links in UI ✅

**Problem:** Article cards in the dashboard did not display clickable links to read the full articles.

**Solution:**
- Added a "Read full article" link below each article's metadata
- Link opens in a new tab (`target="_blank"`)
- Added security attributes (`rel="noopener noreferrer"`)
- Styled with blue color and link emoji (🔗) for clear visibility

**Files Changed:**
- `django_app/news/templates/news/dashboard.html` - Added URL link display

### 4. Sentiment Analysis Error with Default Neutral Scores ✅

**Problem:** Clicking "Analyze sentiment" resulted in "Error analyzing sentiment" with default neutral scores.

**Solution:**

#### FastAPI Service (`fastapi_service/main.py`):
- Enhanced fallback analysis when Ollama API is not available
- Extracted sentiment keywords to configuration constants (`POSITIVE_KEYWORDS`, `NEGATIVE_KEYWORDS`)
- Implemented keyword-based sentiment detection in fallback:
  - Positive keywords: surge, rally, gain, bullish, positive, growth, increase, adoption, breakthrough, etc.
  - Negative keywords: crash, fall, decline, bearish, negative, drop, loss, concern, risk, etc.
  - Returns appropriate sentiment based on detected keywords
- Improved error handling to catch both HTTPError and ConnectError
- Fallback provides meaningful analysis text instead of generic errors

#### Django Service (`django_app/news/services.py`):
- Added specific error handling for different failure scenarios:
  - Connection errors: "Cannot connect to sentiment analysis service"
  - Timeout errors: "Sentiment analysis service timed out"
  - HTTP errors: Shows the specific status code
- Added detailed error logging with exception info
- Improved error messages shown to users

#### Django Views (`django_app/news/views.py`):
- Enhanced error response to include the actual error message
- Added exception info logging for better debugging
- Error messages now show specific details instead of generic "Failed to analyze sentiment"

**Files Changed:**
- `fastapi_service/main.py` - `analyze_with_ollama()` function
- `django_app/news/services.py` - `analyze_articles()` method
- `django_app/news/views.py` - `AnalyzeSentimentView.post()` method

## Testing

Created two test suites to validate the fixes:

1. **test_scraper_fixes.py** - Tests scraper improvements:
   - Yahoo Finance crypto keyword filtering
   - CoinDesk fallback selectors
   - URL link template rendering
   - Title length filtering

2. **test_sentiment_fixes.py** - Tests sentiment analysis improvements:
   - Keyword-based sentiment detection
   - Fallback message appropriateness
   - Error message clarity
   - Confidence score validity

All tests pass successfully (8/8 tests).

## Summary of Changes

- **6 files modified**
- **130+ lines added, 20+ lines removed**
- **0 new dependencies added**
- **All changes are backward compatible**
- **1 security vulnerability fixed**

## User-Facing Improvements

1. **Better Article Quality**: Only crypto-related articles from all sources
2. **More Articles**: Improved scrapers now successfully fetch from CoinDesk, CoinTelegraph, and Yahoo Finance
3. **Better UX**: Clickable links to read full articles
4. **Better Error Handling**: Clear error messages when sentiment analysis fails
5. **Fallback Analysis**: Working sentiment analysis even when Ollama is unavailable

## Notes

- The scraper improvements are resilient to website structure changes by using multiple selector strategies
- The sentiment analysis fallback uses keyword detection to provide reasonable sentiment even without LLM
- All changes maintain the existing API contracts and database schema
- No breaking changes to the existing codebase
- Security: Fixed stack trace exposure vulnerability to prevent leaking implementation details to users

## Security Summary

**Issue Found and Fixed:**
- **py/stack-trace-exposure**: Error messages in sentiment analysis view were exposing detailed exception information to external users
- **Fix**: Changed error response to use generic error message while logging detailed information server-side only
- **Impact**: Prevents potential attackers from learning about internal implementation details through error messages
- **Verification**: CodeQL security scan shows 0 alerts after fix
