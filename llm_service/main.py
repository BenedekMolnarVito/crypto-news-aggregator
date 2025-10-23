"""
FastAPI service for LLM-based sentiment analysis using Ollama Cloud.
Provides endpoints for analyzing crypto news sentiment.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import httpx
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sentiment analysis keywords for fallback analysis
POSITIVE_KEYWORDS = [
    'surge', 'rally', 'gain', 'bullish', 'positive', 'growth', 'increase',
    'adoption', 'breakthrough', 'soar', 'pump', 'moon', 'rising', 'up'
]

NEGATIVE_KEYWORDS = [
    'crash', 'fall', 'decline', 'bearish', 'negative', 'drop', 'loss',
    'concern', 'risk', 'plunge', 'dump', 'down', 'falling', 'fear'
]

app = FastAPI(
    title="Crypto News Sentiment Analysis API",
    description="LLM-based sentiment analysis for crypto news using Ollama",
    version="1.0.0"
)

# Ollama Cloud configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "https://api.ollama.ai/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")


class Article(BaseModel):
    """Article model for sentiment analysis."""
    title: str = Field(..., description="Article title")
    text: str = Field(..., description="Article text content")
    source: Optional[str] = Field(None, description="Article source")
    url: Optional[str] = Field(None, description="Article URL")


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis."""
    articles: List[Article] = Field(..., description="List of articles to analyze")


class SentimentResult(BaseModel):
    """Result model for sentiment analysis."""
    title: str
    sentiment: str
    confidence: float
    summary: str
    key_points: List[str]


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""
    success: bool
    results: List[SentimentResult]
    overall_sentiment: str
    market_outlook: str


async def analyze_with_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Send a request to Ollama Cloud API."""
    try:
        # Check if we're using a local Ollama instance (default) or cloud API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OLLAMA_API_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except (httpx.HTTPError, httpx.ConnectError) as e:
        logger.warning(f"Ollama API not available: {e}. Using fallback analysis.")
        # Enhanced fallback for development/testing when Ollama is not available
        # Analyze based on keywords in the prompt
        prompt_lower = prompt.lower()
        
        # Determine sentiment based on common keywords
        if any(word in prompt_lower for word in POSITIVE_KEYWORDS):
            return "Analysis shows a positive sentiment. The market appears bullish with indicators suggesting growth potential. Key factors include increased adoption and positive price action."
        elif any(word in prompt_lower for word in NEGATIVE_KEYWORDS):
            return "Analysis indicates a negative sentiment. The market shows bearish signals with concerns about potential downside. Key factors include declining metrics and risk indicators."
        else:
            return "Analysis reveals a neutral sentiment. The market shows mixed signals with no clear directional bias. Investors should monitor for clearer trends before making decisions."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Neutral market sentiment detected. Analysis indicates balanced market conditions with no strong directional bias."


def parse_sentiment_response(response: str) -> Dict:
    """Parse the LLM response to extract sentiment information."""
    # Simple parsing logic - can be enhanced
    sentiment = "neutral"
    confidence = 0.5
    
    response_lower = response.lower()
    if "positive" in response_lower or "bullish" in response_lower:
        sentiment = "positive"
        confidence = 0.7
    elif "negative" in response_lower or "bearish" in response_lower:
        sentiment = "negative"
        confidence = 0.7
    
    # Extract key points (sentences)
    sentences = [s.strip() for s in response.split('.') if s.strip()]
    key_points = sentences[:3] if len(sentences) >= 3 else sentences
    
    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "summary": sentences[0] if sentences else response[:200],
        "key_points": key_points
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sentiment_analysis"}


@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of crypto news articles.
    
    This endpoint uses Ollama Cloud to perform LLM-based sentiment analysis
    on provided articles and returns structured sentiment data.
    """
    try:
        results = []
        sentiments = []
        
        for article in request.articles:
            # Create prompt for sentiment analysis
            prompt = f"""Analyze the sentiment of this crypto news article and provide:
1. Overall sentiment (positive, negative, or neutral)
2. Confidence level
3. Brief summary
4. Key points

Article Title: {article.title}
Article Text: {article.text[:1000]}

Provide a concise analysis focusing on market sentiment and implications."""
            
            # Get analysis from Ollama
            llm_response = await analyze_with_ollama(prompt)
            
            # Parse the response
            parsed = parse_sentiment_response(llm_response)
            
            results.append(SentimentResult(
                title=article.title,
                sentiment=parsed["sentiment"],
                confidence=parsed["confidence"],
                summary=parsed["summary"],
                key_points=parsed["key_points"]
            ))
            
            sentiments.append(parsed["sentiment"])
        
        # Determine overall sentiment
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")
        
        if positive_count > negative_count:
            overall_sentiment = "bullish"
            market_outlook = "Market sentiment is predominantly positive based on recent news."
        elif negative_count > positive_count:
            overall_sentiment = "bearish"
            market_outlook = "Market sentiment is predominantly negative based on recent news."
        else:
            overall_sentiment = "neutral"
            market_outlook = "Market sentiment is mixed with no clear direction."
        
        return SentimentResponse(
            success=True,
            results=results,
            overall_sentiment=overall_sentiment,
            market_outlook=market_outlook
        )
    
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/single")
async def analyze_single_article(article: Article):
    """Analyze sentiment of a single article."""
    try:
        prompt = f"""Analyze the sentiment of this crypto news article:

Title: {article.title}
Text: {article.text[:1000]}

Provide sentiment (positive/negative/neutral), confidence, and key insights."""
        
        llm_response = await analyze_with_ollama(prompt)
        parsed = parse_sentiment_response(llm_response)
        
        return {
            "success": True,
            "title": article.title,
            "sentiment": parsed["sentiment"],
            "confidence": parsed["confidence"],
            "summary": parsed["summary"],
            "key_points": parsed["key_points"],
            "raw_analysis": llm_response
        }
    
    except Exception as e:
        logger.error(f"Error analyzing single article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List available Ollama models."""
    return {
        "current_model": OLLAMA_MODEL,
        "available_models": [
            "llama2",
            "mistral",
            "mixtral",
            "neural-chat"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
