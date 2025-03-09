# Crawler Component Documentation

## Overview

The crawler component is built using the `crawl4ai` library and provides asynchronous web crawling capabilities with browser automation. It's designed to systematically explore websites, extract content, and store the data in a Supabase database.

## Key Features

- Asynchronous operation using `asyncio`
- Browser-based crawling with Chromium
- Same-domain link extraction and traversal
- Automatic data persistence to Supabase
- Configurable browser and crawler settings
- Duplicate URL detection
- Error handling and logging

## Architecture

### Main Components

1. **AsyncWebCrawler**: Core crawling engine from crawl4ai
2. **BrowserConfig**: Browser configuration settings
3. **CrawlerRunConfig**: Crawler behavior settings
4. **SupabaseClient**: Database integration

## Configuration

### Browser Configuration

```python
BrowserConfig(
    browser_type="chromium",
    headless=False,
    viewport_width=1080,
    viewport_height=600,
    ignore_https_errors=True,
    java_script_enabled=True,
    verbose=True
)
```

### Crawler Configuration

```python
CrawlerRunConfig(
    magic=True,
    simulate_user=True,
    override_navigator=True,
    verbose=True,
    cache_mode=CacheMode.ENABLED,
    check_robots_txt=True
)
```

## Core Functionality

### crawl_website Function

```python
async def crawl_website(start_url: str) -> list
```

#### Parameters

- `start_url` (str): The initial URL to begin crawling from

#### Returns

- `list`: Collection of successfully crawled page URLs

#### Process Flow

1. Initializes Supabase client and generates unique origin ID
2. Sets up crawling queues and visited URL tracking
3. Configures browser and crawler settings
4. Iteratively processes URLs:
   - Checks for previously visited URLs
   - Verifies if URL is already in database
   - Performs crawling operation
   - Extracts and stores page content
   - Identifies internal links for further crawling

## Data Storage

### Supabase Integration

The crawler stores the following data for each page:

- URL
- HTML content
- Page title
- Origin ID (UUID)

### Storage Process

1. Checks if URL exists in database
2. Extracts HTML and metadata
3. Stores page data with unique origin identifier

## Error Handling

- Exception catching for individual page crawls
- Logging of crawling errors
- Continued operation after individual page failures

## Usage Example

```python
import asyncio

# Start crawling from a specific URL
asyncio.run(crawl_website("https://example.com"))
```

## Dependencies

- `asyncio`: For asynchronous operations
- `crawl4ai`: Core crawling functionality
- `urllib.parse`: URL parsing and validation
- `uuid`: Unique identifier generation
- `python-dotenv`: Environment variable management

## Environment Requirements

- Environment variables loaded from `.env` file
- Supabase credentials configured
- Chromium browser available

## Performance Considerations

- Asynchronous design for efficient crawling
- URL deduplication to prevent redundant crawls
- Database checks to avoid recrawling
- Configurable browser settings for resource management

## Limitations

- Crawls within same domain only
- Requires browser installation
- Memory usage scales with crawl size
- Network-dependent performance

## Best Practices

1. Configure appropriate viewport sizes
2. Enable headless mode for production
3. Implement rate limiting if needed
4. Monitor database storage usage
5. Handle SSL/HTTPS errors appropriately
6. Respect robots.txt directives

## Security Considerations

- HTTPS error handling enabled
- User agent configuration
- Proxy support available
- Cookie and header management
