#!/bin/bash

# LLM Service Development Scripts

function debug_with_docker() {
    echo "Starting LLM Service in debug mode..."
    docker-compose -f docker-compose.yml -f docker-compose.debug.yml up --build sentiment
}

function start_other_services() {
    echo "Starting other services (excluding sentiment)..."
    docker-compose up db scraper webapp nginx
}

function local_development() {
    echo "Starting LLM Service locally..."
    cd llm_service
    pip install -r requirements.txt debugpy
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}

function debug_local() {
    echo "Starting LLM Service in local debug mode..."
    cd llm_service
    python -m debugpy --listen 5678 --wait-for-client -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}

# Check command line argument
case "$1" in
    "docker-debug")
        debug_with_docker
        ;;
    "other-services")
        start_other_services
        ;;
    "local")
        local_development
        ;;
    "local-debug")
        debug_local
        ;;
    *)
        echo "Usage: $0 {docker-debug|other-services|local|local-debug}"
        echo "  docker-debug   - Start LLM service in Docker with debug port"
        echo "  other-services - Start all services except LLM service"
        echo "  local         - Run LLM service locally"
        echo "  local-debug   - Run LLM service locally with debugger"
        exit 1
        ;;
esac