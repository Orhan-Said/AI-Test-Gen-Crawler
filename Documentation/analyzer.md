# Analyzer Component Documentation

## Overview

The analyzer component is a sophisticated system for analyzing web pages and generating comprehensive test cases. It combines HTML parsing, element extraction, test case generation, and Page Object Model (POM) code generation with built-in caching for performance optimization.

## Key Features

- HTML content analysis using BeautifulSoup
- Form extraction and validation
- Page element categorization
- Test case generation for multiple testing types
- POM code generation with TypeScript support
- Caching system for performance optimization
- Comprehensive error handling and logging
- Accessibility and security considerations

## Core Components

### Cache Management

```python
CACHE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".cache"
CACHE_DURATION = timedelta(hours=24)
```

#### Cache Functions

1. **get_cache_key**

   ```python
   def get_cache_key(url: str, html: str) -> str
   ```

   - Generates SHA-256 hash from URL and HTML content
   - Used for unique cache identification

2. **get_cached_result**

   ```python
   def get_cached_result(cache_key: str) -> dict | None
   ```

   - Retrieves cached analysis if available and not expired
   - Handles cache expiration and cleanup

3. **cache_result**
   ```python
   def cache_result(cache_key: str, result: dict)
   ```
   - Stores analysis results with timestamp
   - Manages cache persistence

### HTML Analysis

#### Form Extraction

```python
def extract_forms(html: str) -> list
```

Features:

- Comprehensive form metadata extraction
- Input field analysis
- Validation rules identification
- Accessibility attributes capture

Extracted Form Data:

```python
{
    'action': str,
    'method': str,
    'id': str,
    'class': list,
    'inputs': [
        {
            'type': str,
            'name': str,
            'id': str,
            'required': bool,
            'validation': dict,
            'accessibility': dict
        }
    ]
}
```

#### Page Element Extraction

```python
def extract_page_elements(html: str) -> dict
```

Extracted Elements:

- Links
- Buttons
- Images
- Headings
- Navigation
- Forms

Element Structure:

```python
{
    'links': [
        {
            'text': str,
            'href': str,
            'id': str,
            'class': list,
            'aria_label': str
        }
    ],
    'buttons': [...],
    'images': [...],
    'headings': [...],
    'navigation': {...},
    'forms': [...]
}
```

### Test Generation

#### Main Analysis Function

```python
def analyze_page(html: str, url: str, use_cache: bool = True) -> dict
```

Generated Output:

```python
{
    "testCases": [
        {
            "title": str,
            "category": str,
            "priority": str,
            "preconditions": str,
            "steps": list,
            "expectedResults": dict,
            "edgeCases": list
        }
    ],
    "pomCode": str,
    "metadata": dict
}
```

#### Test Categories

1. **Navigation Tests**

   - Menu accessibility
   - Link functionality
   - Route validation

2. **Form Tests**

   - Input validation
   - Submission handling
   - Error states
   - Accessibility compliance

3. **Image Tests**

   - Alt text verification
   - Loading states
   - Accessibility requirements

4. **Accessibility Tests**
   - ARIA attributes
   - Keyboard navigation
   - Screen reader compatibility

### POM Generation

#### Structure

```typescript
export class PageName {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // Element Getters
  async getNavigation(): Promise<Locator>;
  async getLinks(): Promise<Locator>;
  async getButtons(): Promise<Locator>;
  async getImages(): Promise<Locator>;
  async getForms(): Promise<Locator>;

  // Actions
  async navigateToLink(href: string): Promise<void>;
  async clickButton(text: string): Promise<void>;
  async fillForm(
    formIndex: number,
    data: Record<string, string>
  ): Promise<void>;
  async submitForm(formIndex: number): Promise<void>;

  // Assertions
  async assertNavigationVisible(): Promise<void>;
  async assertLinkExists(text: string): Promise<void>;
  async assertImagesHaveAlt(): Promise<void>;
  async assertFormExists(index: number): Promise<void>;
}
```

## Error Handling

### Validation Checks

- HTML content validation
- URL format validation
- Input parameter type checking
- Cache integrity verification

### Error Types

1. **ValueError**

   - Invalid input parameters
   - Empty or malformed HTML
   - Invalid URL format

2. **CacheError**

   - Cache read/write failures
   - Expired cache handling
   - Cache corruption detection

3. **ParsingError**
   - HTML parsing failures
   - Element extraction issues
   - Structure validation errors

## Best Practices

### Performance Optimization

1. Use caching for frequently accessed pages
2. Implement rate limiting for API calls
3. Optimize HTML parsing operations
4. Handle large DOM structures efficiently

### Test Case Generation

1. Prioritize critical functionality
2. Include edge cases and error scenarios
3. Consider accessibility requirements
4. Implement security testing patterns

### POM Implementation

1. Use meaningful element selectors
2. Implement reusable actions
3. Include comprehensive assertions
4. Follow TypeScript best practices

## Dependencies

- `beautifulsoup4`: HTML parsing
- `langchain_openai`: AI integration
- `python-dotenv`: Environment management
- `logging`: Error tracking
- `pathlib`: File system operations
- `datetime`: Timestamp management
- `hashlib`: Cache key generation
- `json`: Data serialization

## Configuration

### Environment Variables

```
OPENAI_API_KEY=your-api-key
CURRENT_TIME=timestamp
```

### Logging

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Usage Example

```python
# Initialize analyzer
html_content = """
<form action="/login" method="POST">
    <input type="text" id="username" name="username">
    <input type="password" id="password" name="password">
    <input type="submit" id="submit">
</form>
"""
url = "https://example.com/login"

# Analyze page
result = analyze_page(html_content, url)

# Access results
test_cases = result["testCases"]
pom_code = result["pomCode"]
metadata = result["metadata"]
```

## Limitations

1. **HTML Parsing**

   - Complex dynamic content handling
   - JavaScript-rendered content
   - Shadow DOM limitations

2. **Test Generation**

   - Fixed test patterns
   - Limited edge case coverage
   - Basic security testing

3. **POM Generation**
   - Static selector strategies
   - Basic action implementations
   - Limited custom configurations

## Future Enhancements

1. **Analysis Capabilities**

   - Dynamic content analysis
   - JavaScript execution support
   - Advanced security testing

2. **Test Coverage**

   - Custom test templates
   - Advanced edge case detection
   - Performance test generation

3. **POM Features**
   - Custom selector strategies
   - Advanced action patterns
   - Configuration flexibility
