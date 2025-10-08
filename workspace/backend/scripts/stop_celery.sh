#!/bin/bash

# Stop Celery services for Routix Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

print_status "Stopping all Celery services..."

# Stop worker
if [ -f /tmp/celery_worker.pid ]; then
    print_info "Stopping Celery worker..."
    celery -A app.workers.celery_app control shutdown || true
    rm -f /tmp/celery_worker.pid
fi

# Stop beat
if [ -f /tmp/celerybeat.pid ]; then
    print_info "Stopping Celery beat..."
    kill $(cat /tmp/celerybeat.pid) 2>/dev/null || true
    rm -f /tmp/celerybeat.pid /tmp/celerybeat-schedule*
fi

# Stop flower
if [ -f /tmp/flower.pid ]; then
    print_info "Stopping Flower..."
    kill $(cat /tmp/flower.pid) 2>/dev/null || true
    rm -f /tmp/flower.pid
fi

# Kill any remaining celery processes
print_info "Cleaning up any remaining processes..."
pkill -f "celery.*app.workers.celery_app" 2>/dev/null || true

print_status "All Celery services stopped"