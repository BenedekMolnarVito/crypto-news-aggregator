# Contributing to Crypto News Aggregator

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Submitting Changes](#submitting-changes)

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

---

## Getting Started

### Areas for Contribution

- **New Features**: Add new news sources, sentiment models, or UI improvements
- **Bug Fixes**: Fix issues in scraping, analysis, or web interface
- **Documentation**: Improve README, guides, or code comments
- **Testing**: Add unit tests, integration tests, or end-to-end tests
- **Performance**: Optimize scraping, caching, or database queries
- **Security**: Identify and fix security vulnerabilities

### Finding Issues

- Check the [Issues](https://github.com/BenedekMolnarVito/crypto-news-aggregator/issues) page
- Look for labels: `good first issue`, `help wanted`, `bug`, `enhancement`
- Comment on an issue before starting work to avoid duplication

---

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional)
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/crypto-news-aggregator.git
   cd crypto-news-aggregator
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   # Scraper service
   cd scraper_service
   pip install -r requirements.txt
   
   # Sentiment service
   cd ../llm_service
   pip install -r requirements.txt
   
   # Django app
   cd ../django_app
   pip install -r requirements.txt
   ```

5. **Run migrations**
   ```bash
   cd django_app
   python manage.py migrate
   ```

---

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-coinbase-source`
- `fix/scraper-timeout-issue`
- `docs/update-api-documentation`
- `refactor/improve-sentiment-analysis`

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Detailed explanation if needed

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(scraper): add Binance news source
fix(sentiment): handle empty article text
docs(readme): update installation instructions
```

---

## Coding Standards

### Python Style Guide

Follow PEP 8 style guide:
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions and classes

### Code Formatting

Use Black for code formatting:
```bash
pip install black
black scraper_service/scraper.py
```

### Type Hints

Use type hints for function parameters and return values:
```python
def scrape_articles(self, limit: int = 5) -> List[Dict[str, str]]:
    """Scrape articles from source."""
    pass
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md if adding new features
- Add API documentation for new endpoints

Example:
```python
def analyze_sentiment(article: Article) -> SentimentResult:
    """
    Analyze sentiment of a crypto news article.
    
    Args:
        article: Article object containing title and text
        
    Returns:
        SentimentResult with sentiment, confidence, and summary
        
    Raises:
        ValueError: If article text is empty
    """
    pass
```

---

## Testing

### Running Tests

```bash
# Run Django tests
cd django_app
python manage.py test

# Run pytest (if configured)
pytest tests/
```

### Writing Tests

Add tests for new features:

```python
# tests/test_scraper.py
import unittest
from scraper import CryptoNewsScraper

class TestCryptoNewsScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = CryptoNewsScraper()
    
    def test_scrape_coindesk(self):
        articles = self.scraper.scrape_coindesk()
        self.assertIsInstance(articles, list)
        if articles:
            self.assertIn('title', articles[0])
            self.assertIn('url', articles[0])
```

### Integration Testing

Run the integration test script:
```bash
python test_integration.py
```

---

## Submitting Changes

### Before Submitting

1. **Run tests**: Ensure all tests pass
2. **Update documentation**: Add/update relevant docs
3. **Format code**: Run code formatters
4. **Check for errors**: Fix any linting issues
5. **Test locally**: Run the application and test your changes

### Pull Request Process

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to GitHub and create a PR from your branch
   - Use a clear, descriptive title
   - Fill out the PR template
   - Link related issues

3. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] Added unit tests
   - [ ] Tested locally
   - [ ] Integration tests pass
   
   ## Screenshots (if applicable)
   
   ## Checklist
   - [ ] Code follows project style guide
   - [ ] Documentation updated
   - [ ] No breaking changes
   - [ ] All tests pass
   ```

4. **Code Review**
   - Address reviewer feedback
   - Make requested changes
   - Push updates to the same branch

5. **Merge**
   - PR will be merged after approval
   - Delete your branch after merge

---

## Development Tips

### Adding a New News Source

1. Add source URL to `scraper.py`
2. Create scraping method
3. Add source to Django model choices
4. Update README with new source
5. Add tests

Example:
```python
def scrape_new_source(self) -> List[Dict[str, str]]:
    """Scrape articles from new source."""
    try:
        response = requests.get(self.sources['new_source'], headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        # Scraping logic here
        
        return articles
    except Exception as e:
        logger.error(f"Error scraping new source: {e}")
        return []
```

### Improving Sentiment Analysis

Modify the prompts in `llm_service/main.py`:

```python
prompt = f"""Analyze the crypto news article with focus on:
1. Market sentiment (bullish/bearish/neutral)
2. Price impact prediction
3. Key market drivers
4. Risk factors

Article: {article.title}
Text: {article.text[:1000]}

Provide structured analysis."""
```

### Customizing the Dashboard

Edit `django_app/news/templates/news/dashboard.html` to modify the UI.

---

## Security

### Reporting Security Issues

- **Do not** open public issues for security vulnerabilities
- Email security concerns to the maintainers
- Allow time for fixes before disclosure

### Security Best Practices

- Never commit API keys or secrets
- Sanitize user inputs
- Validate external data
- Use HTTPS in production
- Keep dependencies updated

---

## Getting Help

- **Documentation**: Check README, QUICKSTART, and API_DOCS
- **Issues**: Search existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our community channels (if available)

---

## Recognition

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes
- Acknowledged in documentation

Thank you for contributing to Crypto News Aggregator! 🚀
