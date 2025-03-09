# Wikipedia-based RAG Application

This application implements a Retrieval-Augmented Generation (RAG) system that enhances Large Language Model responses with relevant Wikipedia content. The system processes Wikipedia articles, retrieves the most relevant passages based on user queries, and uses OpenAI's API to generate contextually accurate responses.

## Features

- **RAG Implementation**: Combines retrieval of relevant Wikipedia passages with OpenAI's generative capabilities
- **Wikipedia Data Processing**: Efficiently processes and indexes Wikipedia articles
- **Semantic Search**: Finds the most relevant content passages for user queries
- **Asynchronous Processing**: Uses Celery and Redis for efficient task handling
- **Shared Document Storage**: Centralized storage for processed Wikipedia data and indexes

## System Architecture

The application consists of two main components:
- **API Server**: FastAPI application handling HTTP requests and semantic search
- **Background Processing**: Celery workers with Redis as message broker and cache for asynchronous Wikipedia data processing and indexing

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- User Agent string for Wikipedia API requests

## Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a `.env` file in the root directory with the following variables:
```env
USER_AGENT=your-user-agent-string
OPENAI_API_KEY=your-openai-api-key
```

3. Start the application using Docker Compose:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000`

## API Documentation

### Base URL
```
http://localhost:8000
```

### Available Endpoints

#### Health Check
```
GET /health
```
Returns the current status of the application.

#### API Documentation
```
GET /docs
```
Interactive Swagger documentation for all available endpoints.

#### Alternative API Documentation
```
GET /redoc
```
ReDoc version of the API documentation.

## Directory Structure

```
.
├── src/                    # Source code
│   ├── api/               # API endpoints and routes
│   ├── core/              # Core application logic
│   ├── schemas/           # Data models and schemas
│   └── services/          # Business logic and services
├── tests/                 # Test files
├── data/                  # Shared data directory
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker services configuration
├── Dockerfile            # Application container configuration
├── .env                  # Environment variables (you need to create this)
└── .gitignore           # Git ignore rules
```

## Data Storage

The application uses several storage locations:
- `/app/data`: Shared volume for documents and indexes (accessible by all services)
- `/app/logs`: Application logs
- Redis data storage: Persistent Redis data

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| USER_AGENT | User agent string for API requests | Yes |
| OPENAI_API_KEY | OpenAI API authentication key | Yes |
| REDIS_URL | Redis connection URL | No (default: redis://redis:6379/0) |
| CELERY_BROKER_URL | Celery broker URL | No (default: redis://redis:6379/0) |
| CELERY_RESULT_BACKEND | Celery result backend URL | No (default: redis://redis:6379/0) |

## Development

To run the application in development mode:

1. Start the services:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop the application:
```bash
docker-compose down
```

## Monitoring

- Redis health check is configured to run every 5 seconds
- Application logs are available in the `logs` directory
- Celery worker logs can be viewed using `docker-compose logs celery_worker`

## Troubleshooting

1. If Redis fails to start:
   - Check if port 6379 is available
   - Verify Redis data directory permissions

2. If Celery worker fails:
   - Ensure Redis is healthy
   - Check environment variables
   - Verify log permissions

3. If API server is unavailable:
   - Check if port 8000 is free
   - Verify all services are running with `docker-compose ps`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here] 