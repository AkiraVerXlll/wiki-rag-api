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
git clone https://github.com/AkiraVerXlll/trainee-test-assignment.git
cd trainee-test-assignment
```

2. Start the application using Docker Compose with environment variables:
```bash
USER_AGENT="your-user-agent" OPENAI_API_KEY="your-openai-api-key" docker compose up --build
```

The `USER_AGENT` is required by Wikipedia's API for request identification. Use this format:
```
ProjectName/Version (your-email@domain.com)
```
Example: `MyWikiBot/1.0 (example@gmail.com)`

Wikipedia's API requires a proper User Agent for all requests. Without it, the API will reject your requests.

Replace `your-openai-api-key` with your actual OpenAI API key.

The application will be available at `http://localhost:8000`

## API Documentation

The application comes with built-in interactive API documentation that allows you to test all endpoints directly from your browser.

### Base URL
```
http://localhost:8000
```

### Interactive Documentation

#### Swagger UI
```
GET /docs
```
Access the interactive Swagger interface where you can:
- Explore all available endpoints
- Test API calls directly from the browser
- View request/response schemas
- Execute requests with your parameters

### Available Endpoints

#### Process Wikipedia Content
```
POST /api/v1/process
```
Initiates background processing of Wikipedia content for a given topic.

**Request Body:**
```json
{
    "topic": "string",      // Topic to search on Wikipedia (e.g., "Kyiv", "Isaac Newton")
    "document_id": "string" // Unique identifier for the document
}
```

**Response:**
```json
{
    "task_id": "string"     // ID of the background task
}
```

#### Check Task Status
```
GET /api/v1/status/{task_id}
```
Checks the status of a background processing task.

**Parameters:**
- `task_id` (path): ID of the task to check

**Response:**
```json
{
    "status": "string"      // Task status: "pending", "running", "finished", or "failed"
}
```

#### Chat with Document Context
```
POST /api/v1/chat
```
Interact with ChatGPT using the context from a processed Wikipedia document.

**Request Body:**
```json
{
    "session_id": "string",  // Unique session identifier for conversation tracking
    "document_id": "string", // ID of the processed document to use as context
    "text": "string"         // User's message
}
```

**Response:**
```json
{
    "response": "string"     // ChatGPT's response with context from the document
}
```

#### Health Check
```
GET /-/healthy/
```
Checks if the application is running properly.

**Response:**
```json
{}  // Empty response with 200 status code indicates healthy service
```

### Error Responses

All endpoints may return the following error responses:

```json
{
    "error": "string",      // Error message
    "details": {            // Additional error details
        "error": "string"
    }
}
```

Common error status codes:
- `400`: Validation Error
- `404`: Document/Task Not Found
- `500`: Internal Server Error

## Directory Structure

```
.
├── src/                    # Source code
│   ├── api/               # API endpoints and routes
│   ├── core/              # Core application logic
│   ├── schemas/           # Data models and schemas
│   └── services/          # Business logic and services
├── data/                  # Shared data directory
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Application container configuration
└── .dockerignore          # Docker ignore rules
```

## Extensibility

The application is designed to be easily extensible with custom implementations for text processing and data saving. This is achieved through abstract base classes and dependency injection.

### Current Implementations

The application comes with default implementations that can be used as references or replaced with custom ones:

#### Text Processors
Current: `FaissTextProcessor`
- Uses FAISS (Facebook AI Similarity Search) for efficient vector-based similarity search
- Converts text into embeddings for semantic comparison
- Optimized for fast retrieval in large text collections

The text processor interface allows for alternative implementations using different approaches to text vectorization and similarity search. You can implement your own processor using any text embedding model or similarity search algorithm that suits your specific needs.

#### Data Savers
Current: `WikiSaver`
- Saves Wikipedia content in plain text format
- Organizes documents by unique identifiers
- Maintains a simple file-based storage structure

The data saver interface can be implemented to work with any data source, not just Wikipedia. You can create custom implementations to fetch and save data from various sources like other APIs, databases, or file systems.

### Implementing Custom Components

#### Custom Text Processors

To implement your own text processor:

1. Inherit from the base class in `src/services/text_processors/base_text_processor.py`:
```python
from src.services.text_processors.base_text_processor import ITextProcessor

class CustomTextProcessor(ITextProcessor):
    def __init__(self, folder_path: str):
        """
        Initialize processor with the path where indices will be stored
        """
        super().__init__(folder_path)

    def index_exists(self, index: str) -> bool:
        """
        Check if an index with the specified name exists
        """
        pass

    def load_index(self, index: str):
        """
        Load an existing index from storage
        """
        pass

    def create_index(self, text: str, index: str, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Create and save a new index from the provided text
        - Split text into chunks with specified size and overlap
        - Process and index the chunks
        - Save the index for future use
        """
        pass

    def search_mutual_information(self, query: str) -> str:
        """
        Search indexed content for information relevant to the query
        Returns the most relevant text passages
        """
        pass
```

2. Register your implementation in `src/api/dependencies.py`:
```python
def get_custom_text_processor() -> CustomTextProcessor:
    return CustomTextProcessor()

TextProcessor = Annotated[CustomTextProcessor, Depends(get_custom_text_processor)]
```

#### Custom Data Savers

To implement your own data saver:

1. Inherit from the base class in `src/services/additional_data_savers/base_additional_data_saver.py`:
```python
from src.services.additional_data_savers.base_additional_data_saver import IAdditionalDataSaver

class CustomDataSaver(IAdditionalDataSaver):
    def __init__(self, folder_path: str):
        """
        Initialize saver with the path where documents will be stored
        """
        super().__init__(folder_path)

    def save(self, topic: str, document_id: str) -> str:
        """
        Save the content to a text file
        :param topic: The title of the article to save
        :param document_id: The ID to use for naming the saved file
        :return: The full path to the saved text file
        """
        pass
```

2. Register your implementation in `src/api/dependencies.py`:
```python
def get_custom_saver() -> CustomDataSaver:
    return CustomDataSaver()

AdditionalDataSaver = Annotated[CustomDataSaver, Depends(get_custom_saver)]
```

## Data Storage

The application uses several storage locations:
- `/app/data`: Shared volume for documents, sessions and indexes (accessible by all services)
- `/app/logs`: Application logs