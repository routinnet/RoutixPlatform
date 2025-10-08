#!/bin/bash

# Start Celery services for Routix Platform
# Usage: ./scripts/start_celery.sh [worker|beat|flower|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CELERY_APP="app.workers.celery_app"
LOG_LEVEL="info"
CONCURRENCY=4

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

print_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if Redis is running
check_redis() {
    print_info "Checking Redis connection..."
    if python -c "import redis; r=redis.from_url('redis://localhost:6379'); r.ping(); print('Redis OK')" 2>/dev/null; then
        print_status "Redis is running and accessible"
        return 0
    else
        print_error "Redis is not running or not accessible"
        print_info "Please start Redis server: redis-server"
        return 1
    fi
}

# Start Celery worker
start_worker() {
    print_status "Starting Celery worker..."
    print_info "App: $CELERY_APP"
    print_info "Concurrency: $CONCURRENCY"
    print_info "Log Level: $LOG_LEVEL"
    
    exec celery -A $CELERY_APP worker \
        --loglevel=$LOG_LEVEL \
        --concurrency=$CONCURRENCY \
        --queues=template_analysis,generation,cleanup,test \
        --hostname=worker@%h \
        --without-gossip \
        --without-mingle \
        --without-heartbeat
}

# Start Celery Beat scheduler
start_beat() {
    print_status "Starting Celery Beat scheduler..."
    
    exec celery -A $CELERY_APP beat \
        --loglevel=$LOG_LEVEL \
        --scheduler=celery.beat:PersistentScheduler \
        --schedule=/tmp/celerybeat-schedule \
        --pidfile=/tmp/celerybeat.pid
}

# Start Flower monitoring
start_flower() {
    print_status "Starting Flower monitoring dashboard..."
    print_info "Flower will be available at: http://localhost:5555"
    
    exec celery -A $CELERY_APP flower \
        --port=5555 \
        --broker=redis://localhost:6379/0 \
        --basic_auth=admin:routix123 \
        --url_prefix=flower
}

# Start all services in background
start_all() {
    print_status "Starting all Celery services..."
    
    # Create log directory
    mkdir -p logs
    
    # Start worker in background
    print_info "Starting worker in background..."
    celery -A $CELERY_APP worker \
        --loglevel=$LOG_LEVEL \
        --concurrency=$CONCURRENCY \
        --queues=template_analysis,generation,cleanup,test \
        --hostname=worker@%h \
        --pidfile=/tmp/celery_worker.pid \
        --logfile=logs/celery_worker.log \
        --detach
    
    sleep 2
    
    # Start beat in background
    print_info "Starting beat scheduler in background..."
    celery -A $CELERY_APP beat \
        --loglevel=$LOG_LEVEL \
        --scheduler=celery.beat:PersistentScheduler \
        --schedule=/tmp/celerybeat-schedule \
        --pidfile=/tmp/celerybeat.pid \
        --logfile=logs/celery_beat.log \
        --detach
    
    sleep 2
    
    # Start flower in background
    print_info "Starting flower monitoring in background..."
    celery -A $CELERY_APP flower \
        --port=5555 \
        --broker=redis://localhost:6379/0 \
        --basic_auth=admin:routix123 \
        --url_prefix=flower \
        --logging=info \
        --log_file_prefix=logs/flower \
        &
    
    FLOWER_PID=$!
    echo $FLOWER_PID > /tmp/flower.pid
    
    print_status "All services started successfully!"
    print_info "Worker PID file: /tmp/celery_worker.pid"
    print_info "Beat PID file: /tmp/celerybeat.pid"
    print_info "Flower PID file: /tmp/flower.pid"
    print_info "Flower dashboard: http://localhost:5555 (admin:routix123)"
    print_info "Log files in: logs/"
    
    print_warning "To stop all services, run: ./scripts/stop_celery.sh"
}

# Stop all services
stop_all() {
    print_status "Stopping all Celery services..."
    
    # Stop worker
    if [ -f /tmp/celery_worker.pid ]; then
        print_info "Stopping Celery worker..."
        celery -A $CELERY_APP control shutdown || true
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
    
    print_status "All services stopped"
}

# Show service status
show_status() {
    print_info "Celery Services Status:"
    echo
    
    # Check worker
    if [ -f /tmp/celery_worker.pid ]; then
        if ps -p $(cat /tmp/celery_worker.pid) > /dev/null 2>&1; then
            print_status "Worker: Running (PID: $(cat /tmp/celery_worker.pid))"
        else
            print_warning "Worker: PID file exists but process not running"
        fi
    else
        print_warning "Worker: Not running"
    fi
    
    # Check beat
    if [ -f /tmp/celerybeat.pid ]; then
        if ps -p $(cat /tmp/celerybeat.pid) > /dev/null 2>&1; then
            print_status "Beat: Running (PID: $(cat /tmp/celerybeat.pid))"
        else
            print_warning "Beat: PID file exists but process not running"
        fi
    else
        print_warning "Beat: Not running"
    fi
    
    # Check flower
    if [ -f /tmp/flower.pid ]; then
        if ps -p $(cat /tmp/flower.pid) > /dev/null 2>&1; then
            print_status "Flower: Running (PID: $(cat /tmp/flower.pid)) - http://localhost:5555"
        else
            print_warning "Flower: PID file exists but process not running"
        fi
    else
        print_warning "Flower: Not running"
    fi
    
    echo
    print_info "Active queues and tasks:"
    celery -A $CELERY_APP inspect active 2>/dev/null || print_warning "No active workers found"
}

# Main script logic
case "${1:-help}" in
    "worker")
        check_redis || exit 1
        start_worker
        ;;
    "beat")
        check_redis || exit 1
        start_beat
        ;;
    "flower")
        check_redis || exit 1
        start_flower
        ;;
    "all")
        check_redis || exit 1
        start_all
        ;;
    "stop")
        stop_all
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        echo "Routix Celery Service Manager"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  worker    Start Celery worker (foreground)"
        echo "  beat      Start Celery Beat scheduler (foreground)"
        echo "  flower    Start Flower monitoring dashboard (foreground)"
        echo "  all       Start all services (background)"
        echo "  stop      Stop all services"
        echo "  status    Show service status"
        echo "  help      Show this help message"
        echo
        echo "Examples:"
        echo "  $0 all              # Start all services in background"
        echo "  $0 worker           # Start only worker in foreground"
        echo "  $0 status           # Check service status"
        echo "  $0 stop             # Stop all services"
        ;;
esac