#!/bin/bash
# Feedback Processor Theory - Deployment Script
# Automates setup and deployment

set -e  # Exit on error

echo "=========================================="
echo "Feedback Processor Theory Deployment"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the harmonic-demo directory"
    exit 1
fi

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if command -v docker &> /dev/null; then
    print_status "Docker installed: $(docker --version | cut -d' ' -f3)"
else
    print_error "Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_status "Docker Compose installed: $(docker-compose --version | cut -d' ' -f3)"
else
    print_error "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        print_status ".env file created"
        echo ""
        echo -e "${YELLOW}IMPORTANT: Edit .env and add your API keys before continuing!${NC}"
        echo "Required keys:"
        echo "  - OPENAI_API_KEY (required)"
        echo "  - NVAPI_KEY (optional)"
        echo "  - ANTHROPIC_API_KEY (optional)"
        echo ""
        read -p "Press Enter after editing .env file..."
    else
        print_error ".env.example not found. Cannot create .env file."
        exit 1
    fi
fi

# Validate API keys
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-proj-..." ]; then
    print_error "OPENAI_API_KEY not set in .env file"
    echo "Please edit .env and add your OpenAI API key"
    exit 1
else
    print_status "OpenAI API key configured"
fi

echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs backups
print_status "Directories created"

echo ""

# Build Docker images
echo "Building Docker images..."
docker-compose build

if [ $? -eq 0 ]; then
    print_status "Docker images built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

echo ""

# Start services
echo "Starting services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_status "Services started"
else
    print_error "Failed to start services"
    exit 1
fi

echo ""

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Check backend health
if docker-compose ps | grep -q "harmonic-backend.*Up"; then
    print_status "Backend service is running"
else
    print_warning "Backend service may not be ready"
fi

# Check frontend health
if docker-compose ps | grep -q "harmonic-frontend.*Up"; then
    print_status "Frontend service is running"
else
    print_warning "Frontend service may not be ready"
fi

# Check Redis health
if docker-compose ps | grep -q "harmonic-redis.*Up"; then
    print_status "Redis service is running"
else
    print_warning "Redis service may not be ready"
fi

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:8000"
echo "  Backend:  ws://localhost:8765"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo "  View status:     docker-compose ps"
echo ""
echo "To test the deployment:"
echo "  1. Open http://localhost:8000 in your browser"
echo "  2. Click 'Connect' to establish WebSocket connection"
echo "  3. Select an LLM and send a test message"
echo ""

# Offer to show logs
read -p "View live logs? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi