# Nginx Deployment Guide

This guide explains how to deploy the Crypto News Aggregator behind Nginx on your Ubuntu server.

## Configuration

The application is configured to be accessible at:
- **Domain**: vitoscaletta.duckdns.org
- **Dashboard**: http://vitoscaletta.duckdns.org/crypto-news

## Architecture

The nginx container acts as a reverse proxy and routes requests to the appropriate services:

```
Internet → Nginx (Port 80/443) → Backend Services
                ├── /crypto-news → Django App (Port 8080)
                ├── /scraper-api → Scraper Service (Port 5000)
                └── /sentiment-api → Sentiment Service (Port 8000)
```

## Deployment Steps

### 1. Prerequisites

Ensure your Ubuntu server has:
- Docker installed
- Docker Compose installed
- Port 80 and 443 open in firewall
- DuckDNS configured to point to your server's IP

### 2. Clone Repository

```bash
git clone https://github.com/BenedekMolnarVito/crypto-news-aggregator.git
cd crypto-news-aggregator
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

### 4. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 5. Verify Deployment

```bash
# Check nginx is running
curl http://localhost/health

# Check if services are accessible
curl http://localhost/crypto-news
```

## URL Endpoints

### Public Endpoints

- **Dashboard**: http://vitoscaletta.duckdns.org/crypto-news
- **Admin Panel**: http://vitoscaletta.duckdns.org/crypto-news/admin/
- **API Stats**: http://vitoscaletta.duckdns.org/crypto-news/api/stats/
- **Health Check**: http://vitoscaletta.duckdns.org/health

### Optional Direct API Access

- **Scraper API**: http://vitoscaletta.duckdns.org/scraper-api/
- **Sentiment API**: http://vitoscaletta.duckdns.org/sentiment-api/
- **API Docs**: http://vitoscaletta.duckdns.org/sentiment-api/docs

## SSL/HTTPS Configuration

Your domain (vitoscaletta.duckdns.org) already has an SSL certificate configured. To use HTTPS with this application:

### Update Nginx Configuration for SSL

Modify `nginx/nginx.conf` to include your existing SSL certificate paths:

```nginx
server {
    listen 443 ssl http2;
    server_name vitoscaletta.duckdns.org;
    
    # Use your existing SSL certificate paths
    ssl_certificate /path/to/your/fullchain.pem;
    ssl_certificate_key /path/to/your/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... rest of your location blocks (copy from existing config)
}

server {
    listen 80;
    server_name vitoscaletta.duckdns.org;
    return 301 https://$server_name$request_uri;
}
```

### Update Docker Compose for SSL

Mount your existing SSL certificate directory in `docker-compose.yml`:

```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    - /path/to/your/ssl/certs:/etc/ssl/certs:ro
    - nginx_logs:/var/log/nginx
```

Replace `/path/to/your/ssl/certs` with the actual path to your SSL certificate directory.

## Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f webapp
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart nginx
```

### Update Application

```bash
git pull origin main
docker-compose up -d --build
```

### Backup Database

```bash
# Backup PostgreSQL
docker exec crypto_postgres pg_dump -U postgres crypto_news > backup.sql

# Restore
docker exec -i crypto_postgres psql -U postgres crypto_news < backup.sql
```

## Troubleshooting

### Check Service Health

```bash
# Check if all containers are running
docker-compose ps

# Check nginx logs
docker-compose logs nginx

# Check webapp logs
docker-compose logs webapp
```

### Test Nginx Configuration

```bash
docker exec crypto_nginx nginx -t
```

### Reload Nginx Configuration

```bash
docker exec crypto_nginx nginx -s reload
```

### Common Issues

**Issue**: Cannot access at /crypto-news
**Solution**: Ensure DJANGO_SCRIPT_NAME environment variable is set in docker-compose.yml

**Issue**: Static files not loading
**Solution**: Run collectstatic inside webapp container:
```bash
docker exec crypto_webapp python manage.py collectstatic --noinput
```

**Issue**: 502 Bad Gateway
**Solution**: Check if backend services are running:
```bash
docker-compose ps
docker-compose logs webapp
```

## Firewall Configuration

If using UFW on Ubuntu:

```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

## Performance Tuning

### Nginx Worker Processes

Edit `nginx/nginx.conf` and add at the top:

```nginx
worker_processes auto;
worker_connections 1024;
```

### Enable Gzip Compression

Add to nginx server block:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

### Enable Caching

Add to nginx location blocks:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Monitoring

### Check Resource Usage

```bash
docker stats
```

### Check Disk Usage

```bash
docker system df
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

## Security Recommendations

1. **Change default passwords** in `.env` file
2. **Configure SSL certificate paths** in nginx configuration (SSL already exists on domain)
3. **Set up firewall rules** to restrict access
4. **Regular updates**: Keep Docker images updated
5. **Monitor logs**: Set up log monitoring and alerts
6. **Backup regularly**: Automate database backups
7. **Use secrets management**: Consider Docker secrets for sensitive data

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review nginx configuration: `nginx/nginx.conf`
- Verify environment variables in `.env`
- Check GitHub repository for updates
