# API Component Documentation

## Overview

The API component provides a FastAPI-based REST interface for the test generation system. It handles frontend communication, CORS configuration, and asynchronous task management for website crawling and test generation.

## Key Features

- RESTful API endpoints
- CORS support for frontend integration
- Asynchronous task processing
- Request validation using Pydantic
- FastAPI framework utilization
- Cross-origin resource sharing

## Architecture

### Core Components

1. **FastAPI Application**

   ```python
   app = FastAPI()
   ```

2. **Request Model**

   ```python
   class CrawlRequest(BaseModel):
       url: str
   ```

3. **CORS Configuration**

   ```python
   origins = ["http://localhost:3000"]

   app.add_middleware(
       CORSMiddleware,
       allow_origins=origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## API Endpoints

### 1. OPTIONS /crawl

```python
@app.options("/crawl")
async def options():
    """Handle pre-flight requests for CORS."""
    return {"message": "OPTIONS request accepted"}
```

Purpose:

- Handles CORS pre-flight requests
- Enables cross-origin communication
- Validates request headers

### 2. POST /crawl

```python
@app.post("/crawl")
async def start_crawl(request: CrawlRequest):
    """Start crawling and test generation for the given URL."""
    asyncio.create_task(process_website(request.url))
    return {
        "message": "Crawling and test generation started",
        "url": request.url
    }
```

Features:

- Asynchronous task creation
- Request validation
- Non-blocking operation
- Task status reporting

## Request/Response Format

### Crawl Request

```json
{
  "url": "https://example.com"
}
```

### Crawl Response

```json
{
  "message": "Crawling and test generation started",
  "url": "https://example.com"
}
```

## CORS Configuration

### Allowed Origins

```python
origins = [
    "http://localhost:3000",
]
```

### Middleware Settings

- Allow specified origins
- Enable credentials
- Allow all methods
- Allow all headers

## Dependencies

- `fastapi`: Web framework
- `pydantic`: Data validation
- `asyncio`: Asynchronous operations
- `uvicorn`: ASGI server
- `main`: Core processing module

## Usage

### Starting the Server

```bash
uvicorn api:app --reload
```

Options:

- `--reload`: Enable auto-reload for development
- Default port: 8000
- Default host: localhost

### Making Requests

```python
# Using Python requests
import requests

response = requests.post(
    "http://localhost:8000/crawl",
    json={"url": "https://example.com"}
)
print(response.json())
```

```javascript
// Using JavaScript fetch
fetch('http://localhost:8000/crawl', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com',
  }),
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Error Handling

### Request Validation

- Invalid URL format
- Missing required fields
- Type mismatches

### CORS Errors

- Origin not allowed
- Method not allowed
- Headers not allowed

### Runtime Errors

- Connection failures
- Processing errors
- Timeout issues

## Best Practices

### API Design

1. RESTful principles
2. Clear endpoint naming
3. Proper HTTP methods
4. Consistent response format

### Security

1. CORS configuration
2. Input validation
3. Error handling
4. Rate limiting

### Performance

1. Asynchronous processing
2. Non-blocking operations
3. Resource management
4. Task queuing

## Limitations

1. **Endpoint Coverage**

   - Limited to crawling initiation
   - No status checking
   - No result retrieval

2. **CORS Configuration**

   - Fixed origin list
   - Development-focused setup
   - Limited security options

3. **Task Management**
   - Basic async implementation
   - No progress tracking
   - Limited error reporting

## Future Enhancements

1. **API Extensions**

   - Status endpoint
   - Results endpoint
   - Cancel operation
   - Progress tracking

2. **Security Features**

   - Authentication
   - Rate limiting
   - Request validation
   - Logging system

3. **Monitoring**
   - Health checks
   - Performance metrics
   - Error tracking
   - Usage statistics

## Configuration Options

### Server Settings

```python
# uvicorn configuration
{
    "host": "0.0.0.0",
    "port": 8000,
    "reload": true,
    "workers": 1,
    "log_level": "info"
}
```

### CORS Settings

```python
# CORS configuration
{
    "allow_origins": ["http://localhost:3000"],
    "allow_credentials": true,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}
```

## Integration Guide

### Frontend Integration

1. Configure API base URL
2. Handle CORS requirements
3. Implement error handling
4. Add progress indicators

### Backend Integration

1. Import required modules
2. Configure FastAPI app
3. Set up CORS middleware
4. Implement endpoint handlers

## Testing

### Manual Testing

```bash
# Using curl
curl -X POST http://localhost:8000/crawl \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

### Automated Testing

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_crawl_endpoint():
    response = client.post(
        "/crawl",
        json={"url": "https://example.com"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
```
