#!/bin/bash

set -e

echo "🚀 Setting up Peerless Website Development Environment"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

current_branch=$(git branch --show-current)
if [ "$current_branch" != "website" ]; then
    print_warning "You're not on the 'website' branch. Current branch: $current_branch"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
print_status "Checking for required tools..."

DOCKER_AVAILABLE=false
DOCKER_COMPOSE_AVAILABLE=false

if command -v docker &> /dev/null; then
    DOCKER_AVAILABLE=true
    print_success "Docker is available"
else
    print_warning "Docker is not installed. Docker services will be skipped."
fi

if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_AVAILABLE=true
    print_success "Docker Compose is available"
else
    print_warning "Docker Compose is not installed. Docker services will be skipped."
fi

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_success "Node.js and npm are available"

print_status "Installing frontend dependencies..."
cd frontend
npm install
print_success "Frontend dependencies installed"

print_status "Running frontend tests..."
npm test
if [ $? -eq 0 ]; then
    print_success "Frontend tests passed"
else
    print_error "Frontend tests failed"
    exit 1
fi

cd ..

print_status "Running integration tests..."
./test_integration.sh
if [ $? -eq 0 ]; then
    print_success "Integration tests passed"
else
    print_warning "Some integration tests failed, but continuing setup"
fi
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
POSTGRES_USER=peerless
POSTGRES_PASSWORD=peerless_dev_password
POSTGRES_DB=peerless
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

DISCORD_CLIENT_ID=your_discord_client_id_here
DISCORD_CLIENT_SECRET=your_discord_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:8000/api/auth/callback

TOKEN=your_bot_token_here
EOF
    print_success ".env file created"
    print_warning "Please update the Discord OAuth credentials in .env file"
else
    print_status ".env file already exists"
fi

if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
    print_status "Starting website services (database, redis, api, frontend)..."
    docker-compose --profile website up -d

    print_status "Waiting for services to start..."
    sleep 10

    if docker-compose ps | grep -q "frontend.*Up"; then
        print_success "Frontend service is running"
    else
        print_error "Frontend service failed to start"
    fi

    if docker-compose ps | grep -q "api.*Up"; then
        print_success "API service is running"
    else
        print_warning "API service may not be running properly"
    fi

    print_success "Website development environment is ready!"
    echo
    echo "📝 Next steps:"
    echo "  • Frontend: http://localhost:5173"
    echo "  • API: http://localhost:8000"
    echo "  • To stop services: docker-compose --profile website down"
    echo "  • To view logs: docker-compose --profile website logs -f"
else
    print_warning "Docker services are not available. You can still develop the frontend locally."
    echo
    echo "📝 To start frontend development:"
    echo "  • cd frontend"
    echo "  • npm run dev"
    echo "  • Open http://localhost:5173"
    echo
    echo "📝 To run tests:"
    echo "  • cd frontend"
    echo "  • npm test"
fi

echo
print_status "Happy coding! 🎉"
