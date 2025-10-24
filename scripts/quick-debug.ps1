# Quick Start Guide for Debugging All Services

Write-Host "=== Crypto News Aggregator - Debug Setup ===" -ForegroundColor Green

Write-Host "`n🔧 Available Debug Options:" -ForegroundColor Yellow
Write-Host "1. Docker Debug Mode (Recommended)" -ForegroundColor Cyan
Write-Host "2. Local Development Mode" -ForegroundColor Cyan
Write-Host "3. Hybrid Mode (Infrastructure + Local Services)" -ForegroundColor Cyan

$choice = Read-Host "`nSelect option (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`n🐳 Starting ALL services in Docker Debug Mode..." -ForegroundColor Green
        Write-Host "Debug ports:" -ForegroundColor Yellow
        Write-Host "  - LLM Service: 5678" -ForegroundColor White
        Write-Host "  - Scraper Service: 5679" -ForegroundColor White
        Write-Host "  - Django Web App: 5680" -ForegroundColor White
        Write-Host "`nStarting services... This may take a few minutes." -ForegroundColor Yellow
        
        docker-compose -f docker-compose.yml -f docker-compose.debug.yml up --build
        
        Write-Host "`n✅ Services started! Now:" -ForegroundColor Green
        Write-Host "1. Go to Run and Debug (Ctrl+Shift+D)" -ForegroundColor White
        Write-Host "2. Select 'Debug All Services (Docker)'" -ForegroundColor White
        Write-Host "3. Click Start Debugging (F5)" -ForegroundColor White
    }
    "2" {
        Write-Host "`n💻 Starting services locally..." -ForegroundColor Green
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        
        # Start database
        Write-Host "Starting database..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-Command", "docker-compose up db" -WindowStyle Minimized
        
        Start-Sleep 5
        
        # Install dependencies for all services
        Set-Location llm_service
        pip install -r requirements.txt debugpy
        Set-Location ../scraper_service  
        pip install -r requirements.txt debugpy
        Set-Location ../django_app
        pip install -r requirements.txt debugpy
        Set-Location ..
        
        Write-Host "`n✅ Dependencies installed! Now:" -ForegroundColor Green
        Write-Host "1. Go to Run and Debug (Ctrl+Shift+D)" -ForegroundColor White
        Write-Host "2. Select 'Debug All Services (Local)'" -ForegroundColor White
        Write-Host "3. Click Start Debugging (F5)" -ForegroundColor White
    }
    "3" {
        Write-Host "`n🔀 Starting infrastructure services..." -ForegroundColor Green
        docker-compose up db nginx
        
        Write-Host "`n✅ Infrastructure started! Now you can:" -ForegroundColor Green
        Write-Host "1. Run individual services locally" -ForegroundColor White
        Write-Host "2. Use VS Code debug configurations" -ForegroundColor White
        Write-Host "3. Set breakpoints and debug!" -ForegroundColor White
    }
    default {
        Write-Host "`n❌ Invalid option. Please run the script again." -ForegroundColor Red
    }
}

Write-Host "`n📚 Quick Debug Tips:" -ForegroundColor Yellow
Write-Host "- Set breakpoints by clicking left margin in editor" -ForegroundColor White
Write-Host "- Use F10 (step over), F11 (step into), F5 (continue)" -ForegroundColor White
Write-Host "- Check Variables panel for variable values" -ForegroundColor White
Write-Host "- Use Debug Console to evaluate expressions" -ForegroundColor White

Write-Host "`n🌐 Service URLs:" -ForegroundColor Yellow
Write-Host "- LLM Service: http://localhost:8001" -ForegroundColor White
Write-Host "- Scraper Service: http://localhost:5000" -ForegroundColor White  
Write-Host "- Django Web App: http://localhost:8000" -ForegroundColor White
Write-Host "- Nginx (Production-like): http://localhost:8888" -ForegroundColor White