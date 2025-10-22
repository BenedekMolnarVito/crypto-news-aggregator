# Deployment Guide

This guide covers deploying the Crypto News Aggregator to production environments.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Cloud Deployment](#cloud-deployment)
3. [Security Considerations](#security-considerations)
4. [Performance Optimization](#performance-optimization)
5. [Monitoring and Logging](#monitoring-and-logging)

---

## Docker Deployment

### Production Docker Compose

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  scraper:
    build: ./scraper_service
    container_name: crypto_scraper_prod
    restart: always
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    networks:
      - crypto_network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  sentiment:
    build: ./fastapi_service
    container_name: crypto_sentiment_prod
    restart: always
    environment:
      - OLLAMA_API_URL=${OLLAMA_API_URL}
      - OLLAMA_MODEL=${OLLAMA_MODEL}
    networks:
      - crypto_network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  webapp:
    build: ./django_app
    container_name: crypto_webapp_prod
    restart: always
    environment:
      - SCRAPER_SERVICE_URL=http://scraper:5000
      - SENTIMENT_SERVICE_URL=http://sentiment:8000
      - DJANGO_SETTINGS_MODULE=crypto_sentiment.settings
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - scraper
      - sentiment
    networks:
      - crypto_network
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - db_volume:/app/db.sqlite3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  nginx:
    image: nginx:alpine
    container_name: crypto_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/usr/share/nginx/html/static
      - media_volume:/usr/share/nginx/html/media
    depends_on:
      - webapp
    networks:
      - crypto_network

networks:
  crypto_network:
    driver: bridge

volumes:
  static_volume:
  media_volume:
  db_volume:
```

### Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream webapp {
        server webapp:8080;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://webapp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /usr/share/nginx/html/static/;
        }

        location /media/ {
            alias /usr/share/nginx/html/media/;
        }
    }

    # SSL configuration (uncomment when SSL is set up)
    # server {
    #     listen 443 ssl;
    #     server_name yourdomain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     
    #     location / {
    #         proxy_pass http://webapp;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #     }
    # }
}
```

### Deploy

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## Cloud Deployment

### AWS Deployment (ECS)

1. **Create ECR repositories**
   ```bash
   aws ecr create-repository --repository-name crypto-scraper
   aws ecr create-repository --repository-name crypto-sentiment
   aws ecr create-repository --repository-name crypto-webapp
   ```

2. **Build and push images**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build and push
   docker build -t crypto-scraper ./scraper_service
   docker tag crypto-scraper:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-scraper:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-scraper:latest
   ```

3. **Create ECS task definitions and services**

### Google Cloud Platform (Cloud Run)

```bash
# Build and deploy scraper
gcloud builds submit --tag gcr.io/PROJECT_ID/crypto-scraper ./scraper_service
gcloud run deploy crypto-scraper --image gcr.io/PROJECT_ID/crypto-scraper --platform managed

# Build and deploy sentiment service
gcloud builds submit --tag gcr.io/PROJECT_ID/crypto-sentiment ./fastapi_service
gcloud run deploy crypto-sentiment --image gcr.io/PROJECT_ID/crypto-sentiment --platform managed

# Build and deploy webapp
gcloud builds submit --tag gcr.io/PROJECT_ID/crypto-webapp ./django_app
gcloud run deploy crypto-webapp --image gcr.io/PROJECT_ID/crypto-webapp --platform managed
```

### Heroku Deployment

```bash
# Create apps
heroku create crypto-scraper
heroku create crypto-sentiment
heroku create crypto-webapp

# Deploy each service
cd scraper_service && git push heroku main
cd ../fastapi_service && git push heroku main
cd ../django_app && git push heroku main

# Set environment variables
heroku config:set OLLAMA_API_URL=... --app crypto-sentiment
heroku config:set SECRET_KEY=... --app crypto-webapp
```

---

## Security Considerations

### 1. Environment Variables

Never commit sensitive data. Use environment variables:

```bash
# Production .env
SECRET_KEY=<generate-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://...
OLLAMA_API_URL=https://api.ollama.ai/api/generate
OLLAMA_API_KEY=<your-api-key>
```

### 2. Django Security Settings

Update `settings.py` for production:

```python
# Security settings
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 3. Database Security

- PostgreSQL is now used by default
- Enable SSL connections in production
- Use strong passwords
- Regular backups
- Restrict database access to application network only

### 4. API Security

- Implement API key authentication
- Add rate limiting
- Use CORS properly
- Enable request validation

---

## Performance Optimization

### 1. Caching

Add Redis for caching:

```yaml
# docker-compose.prod.yml
redis:
  image: redis:alpine
  restart: always
  networks:
    - crypto_network
```

Update Django settings:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 2. Database Optimization

```python
# Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['-scraped_at']),
        models.Index(fields=['sentiment']),
    ]
```

### 3. Async Task Queue

Use Celery for background tasks:

```python
# tasks.py
from celery import shared_task

@shared_task
def scrape_news_task():
    scraper = CryptoNewsScraper()
    return scraper.scrape_all()

@shared_task
def analyze_sentiment_task(article_ids):
    # Analyze articles asynchronously
    pass
```

---

## Monitoring and Logging

### 1. Application Monitoring

Use Sentry for error tracking:

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=1.0,
)
```

### 2. Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/crypto-news/app.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

### 3. Health Checks

Add health check endpoints:

```python
@app.route('/health/live')
def liveness():
    return jsonify({'status': 'alive'}), 200

@app.route('/health/ready')
def readiness():
    # Check database connection, external services
    return jsonify({'status': 'ready'}), 200
```

### 4. Metrics

Use Prometheus for metrics:

```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"
```

---

## Backup and Recovery

### Database Backups

```bash
# Backup
docker exec crypto_webapp_prod python manage.py dumpdata > backup.json

# Restore
docker exec -i crypto_webapp_prod python manage.py loaddata < backup.json
```

### Volume Backups

```bash
# Backup volumes
docker run --rm -v crypto_db_volume:/data -v $(pwd):/backup ubuntu tar czf /backup/db_backup.tar.gz /data

# Restore volumes
docker run --rm -v crypto_db_volume:/data -v $(pwd):/backup ubuntu tar xzf /backup/db_backup.tar.gz -C /
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose with replicas
services:
  scraper:
    deploy:
      replicas: 3
      
  webapp:
    deploy:
      replicas: 2
```

### Load Balancing

Use Nginx or HAProxy for load balancing across instances.

---

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and redeploy
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker exec crypto_webapp_prod python manage.py migrate
```

### Zero-Downtime Deployment

Use blue-green deployment or rolling updates with orchestration tools like Kubernetes.

---

## Troubleshooting

### Common Issues

1. **Service connectivity**: Check Docker network configuration
2. **Database migrations**: Run migrations after code updates
3. **SSL issues**: Verify certificate configuration
4. **Performance**: Monitor resource usage and scale accordingly

### Debug Mode

Enable temporary debug logging:

```bash
docker-compose -f docker-compose.prod.yml logs -f webapp
```

---

## Support

For deployment assistance:
- Check logs: `docker-compose logs -f`
- Review configuration files
- Consult cloud provider documentation
- Open an issue on GitHub
