# Development Scripts for All Services

## Debug ALL services with Docker Compose
Write-Host "Starting ALL services in debug mode..."
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up --build

## Debug specific services
Write-Host "Debug LLM Service only..."
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up --build sentiment

Write-Host "Debug Scraper Service only..."
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up --build scraper

Write-Host "Debug Django Web App only..."
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up --build webapp

## Start infrastructure only (for local development)
Write-Host "Starting infrastructure services only..."
docker-compose up db nginx

## Local development for all services
Write-Host "Starting ALL services locally..."

# Start database
Start-Job -ScriptBlock { docker-compose up db }

# Wait for database
Start-Sleep 10

# Start services locally
Start-Job -ScriptBlock { 
    Set-Location llm_service
    pip install -r requirements.txt debugpy
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}

Start-Job -ScriptBlock { 
    Set-Location scraper_service
    pip install -r requirements.txt debugpy
    $env:FLASK_ENV="development"
    $env:FLASK_DEBUG="true"
    python app.py
}

Start-Job -ScriptBlock { 
    Set-Location django_app
    pip install -r requirements.txt debugpy
    $env:DJANGO_SETTINGS_MODULE="crypto_sentiment.settings"
    $env:DEBUG="True"
    $env:DB_HOST="localhost"
    python manage.py runserver 0.0.0.0:8000
}

## Debug mode local for all services
Write-Host "Starting ALL services in local debug mode..."

# LLM Service Debug
Start-Job -ScriptBlock { 
    Set-Location llm_service
    python -m debugpy --listen 5678 --wait-for-client -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}

# Scraper Service Debug
Start-Job -ScriptBlock { 
    Set-Location scraper_service
    $env:FLASK_ENV="development"
    $env:FLASK_DEBUG="true"
    python -m debugpy --listen 5679 --wait-for-client app.py
}

# Django Web App Debug
Start-Job -ScriptBlock { 
    Set-Location django_app
    $env:DJANGO_SETTINGS_MODULE="crypto_sentiment.settings"
    $env:DEBUG="True"
    $env:DB_HOST="localhost"
    python -m debugpy --listen 5680 --wait-for-client manage.py runserver 0.0.0.0:8000
}