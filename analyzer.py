from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
import os
from dotenv import load_dotenv
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".cache"
CACHE_DURATION = timedelta(hours=24)
RATE_LIMIT_DELAY = 1  # seconds between API calls
last_api_call = datetime.min

# Ensure cache directory exists
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_key(url, html):
    """Generate a unique cache key based on URL and HTML content."""
    content = f"{url}{html}".encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def get_cached_result(cache_key):
    """Retrieve cached result if it exists and is not expired."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if not cache_file.exists():
        return None

    try:
        with cache_file.open('r') as f:
            cached_data = json.load(f)

        cached_time = datetime.fromisoformat(cached_data['timestamp'])
        if datetime.now() - cached_time > CACHE_DURATION:
            cache_file.unlink()  # Remove expired cache
            return None

        return cached_data['result']
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
        return None


def cache_result(cache_key, result):
    """Cache the analysis result."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        with cache_file.open('w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        logger.warning(f"Cache write error: {e}")


# Load environment variables
load_dotenv()

# Validate API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize ChatOpenAI with proper configuration
try:
    llm = ChatOpenAI(
        model="gpt-4",
        api_key=api_key,
        temperature=0
    )
except Exception as e:
    logger.error(f"Failed to initialize ChatOpenAI: {e}")
    raise


def extract_forms(html):
    """
    Extract forms and their inputs from HTML using BeautifulSoup.
    Includes comprehensive form metadata for better test generation.

    Args:
        html (str): The HTML content of the page.

    Returns:
        list: List of structured form data.

    Raises:
        ValueError: If HTML content is empty or invalid.
    """
    if not html or not html.strip():
        raise ValueError("Empty HTML content provided")

    try:
        soup = BeautifulSoup(html, 'html.parser')
        forms = soup.find_all('form')
        structured_forms = []

        for form in forms:
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'id': form.get('id', ''),
                'class': form.get('class', []),
                'inputs': [],
                'validation': {
                    'novalidate': form.get('novalidate') is not None,
                    'enctype': form.get('enctype', 'application/x-www-form-urlencoded')
                }
            }

            # Process all form controls
            for control in form.find_all(['input', 'select', 'textarea', 'button']):
                input_data = {
                    'type': control.get('type', 'text' if control.name == 'input' else control.name),
                    'name': control.get('name', ''),
                    'id': control.get('id', ''),
                    'required': control.get('required') is not None,
                    'disabled': control.get('disabled') is not None,
                    'readonly': control.get('readonly') is not None,
                    'maxlength': control.get('maxlength', ''),
                    'minlength': control.get('minlength', ''),
                    'pattern': control.get('pattern', ''),
                    'placeholder': control.get('placeholder', ''),
                    'value': control.get('value', ''),
                    'class': control.get('class', [])
                }

                # Get associated label text
                label = None
                if input_data['id']:
                    label = form.find('label', attrs={'for': input_data['id']})
                if not label and control.parent.name == 'label':
                    label = control.parent
                input_data['label'] = label.get_text(
                    strip=True) if label else ''

                # Additional attributes for specific input types
                if input_data['type'] in ['number', 'range']:
                    input_data.update({
                        'min': control.get('min', ''),
                        'max': control.get('max', ''),
                        'step': control.get('step', '')
                    })
                elif input_data['type'] == 'select':
                    input_data['options'] = [
                        {'value': opt.get('value', ''),
                         'text': opt.get_text(strip=True),
                         'selected': opt.get('selected') is not None}
                        for opt in control.find_all('option')
                    ]

                form_data['inputs'].append(input_data)

            structured_forms.append(form_data)

        return structured_forms

    except Exception as e:
        logger.error(f"Error extracting forms: {str(e)}")
        raise ValueError(f"Failed to parse HTML content: {str(e)}")


prompt = PromptTemplate(
    input_variables=["forms", "url"],
    template="""
You are an expert QA engineer specializing in web form testing, accessibility, and security. Given the following forms extracted from the web page at {url}, generate comprehensive test cases and a Page Object Model (POM) class in TypeScript for Playwright.

Consider the following aspects in your test cases:
1. Functional Testing:
   - Valid/invalid inputs for each field based on validation rules
   - Required field validation
   - Form submission with different combinations
   - Error message validation
   
2. Accessibility Testing:
   - ARIA attributes and roles
   - Keyboard navigation
   - Screen reader compatibility
   - Focus management
   
3. Security Testing:
   - XSS prevention
   - CSRF protection
   - SQL injection prevention
   - Input sanitization
   
4. Edge Cases:
   - Boundary value analysis
   - Network conditions
   - Browser compatibility
   - Mobile responsiveness

Output in JSON format:
{{
  "testCases": [
    {{
      "title": "Test case title",
      "category": "functional|accessibility|security|edge",
      "priority": "high|medium|low",
      "preconditions": "Preconditions",
      "steps": [
        {{
          "action": "fill|click|press|focus|blur|wait|assert",
          "field": "field identifier",
          "value": "input value if applicable",
          "description": "Step description"
        }}
      ],
      "expectedResults": {{
        "type": "redirect|elementVisible|elementHidden|validation|error|success",
        "details": {{
          "message": "Expected message or state",
          "selector": "Element selector if applicable",
          "url": "Expected URL if applicable"
        }}
      }},
      "testData": {{
        "valid": ["list of valid test values"],
        "invalid": ["list of invalid test values"]
      }},
      "accessibility": {{
        "wcag": ["relevant WCAG criteria"],
        "ariaRoles": ["expected ARIA roles"]
      }},
      "security": {{
        "vectors": ["potential attack vectors"],
        "mitigations": ["expected security measures"]
      }}
    }}
  ],
  "pomCode": "TypeScript POM class code with accessibility and security considerations"
}}

Forms:
{forms}
"""
)


def extract_page_elements(html):
    """
    Extract various page elements for testing.
    """
    if not html or not isinstance(html, str):
        raise ValueError("Invalid HTML content provided")

    soup = BeautifulSoup(html, 'html.parser')
    elements = {
        'links': [],
        'buttons': [],
        'images': [],
        'headings': [],
        'navigation': [],
        'forms': extract_forms(html) if html else []
    }

    # Extract links
    for link in soup.find_all('a'):
        elements['links'].append({
            'text': link.get_text(strip=True),
            'href': link.get('href', ''),
            'id': link.get('id', ''),
            'class': link.get('class', []),
            'aria_label': link.get('aria-label', '')
        })

    # Extract buttons
    for button in soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]']):
        elements['buttons'].append({
            'text': button.get_text(strip=True) if button.name == 'button' else button.get('value', ''),
            'type': button.get('type', 'button'),
            'id': button.get('id', ''),
            'class': button.get('class', []),
            'disabled': button.get('disabled') is not None
        })

    # Extract images
    for img in soup.find_all('img'):
        elements['images'].append({
            'src': img.get('src', ''),
            'alt': img.get('alt', ''),
            'id': img.get('id', ''),
            'class': img.get('class', [])
        })

    # Extract headings
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        elements['headings'].append({
            'level': int(heading.name[1]),
            'text': heading.get_text(strip=True),
            'id': heading.get('id', ''),
            'class': heading.get('class', [])
        })

    # Extract navigation
    nav = soup.find('nav')
    if nav:
        elements['navigation'] = {
            'items': [{'text': item.get_text(strip=True), 'href': item.get('href', '')}
                      for item in nav.find_all('a')],
            'aria_label': nav.get('aria-label', ''),
            'id': nav.get('id', ''),
            'class': nav.get('class', [])
        }

    return elements


def analyze_page(html, url, use_cache=True):
    """
    Analyze a page's HTML to generate comprehensive test cases and POM code.
    Includes validation for accessibility and security considerations.

    Args:
        html (str): The HTML content.
        url (str): The page URL.

    Returns:
        dict: Test cases and POM code in JSON format.

    Raises:
        ValueError: If inputs are invalid or processing fails.
    """
    if not html or not isinstance(html, str):
        raise ValueError("Invalid HTML content provided")
    if not url or not isinstance(url, str):
        raise ValueError("Invalid URL provided")

    try:
        # Check cache first
        if use_cache:
            cache_key = get_cache_key(url, html)
            cached_result = get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Using cached result for {url}")
                return cached_result

        # Extract all page elements
        page_elements = extract_page_elements(html)

        # Generate test cases based on page elements
        test_cases = []

        # Navigation tests
        if page_elements['navigation']:
            test_cases.append({
                "title": "Navigation Menu Accessibility",
                "category": "accessibility",
                "priority": "high",
                "preconditions": "Navigation menu is present on the page",
                "steps": [
                    {
                        "action": "assert",
                        "field": "nav",
                        "description": "Verify navigation menu is present and accessible"
                    }
                ],
                "expectedResults": {
                    "type": "elementVisible",
                    "details": {
                        "selector": "nav",
                        "accessibility": True
                    }
                },
                "edgeCases": ["Navigation menu not rendered", "Navigation menu not keyboard accessible"]
            })

        # Link tests
        if page_elements['links']:
            test_cases.append({
                "title": "Link Functionality",
                "category": "functional",
                "priority": "high",
                "preconditions": "Page contains clickable links",
                "steps": [
                    {
                        "action": "click",
                        "field": "a",
                        "description": "Click each link and verify navigation"
                    }
                ],
                "expectedResults": {
                    "type": "navigation",
                    "details": {
                        "verify": "href destination"
                    }
                },
                "edgeCases": ["Link href is invalid", "Link target page not found"]
            })

        # Image tests
        if page_elements['images']:
            test_cases.append({
                "title": "Image Accessibility",
                "category": "accessibility",
                "priority": "high",
                "preconditions": "Page contains images",
                "steps": [
                    {
                        "action": "assert",
                        "field": "img",
                        "description": "Verify all images have alt text"
                    }
                ],
                "expectedResults": {
                    "type": "attribute",
                    "details": {
                        "attribute": "alt",
                        "present": True
                    }
                },
                "edgeCases": ["Missing alt text", "Empty alt text", "Non-descriptive alt text"]
            })

        # Form tests
        if page_elements['forms']:
            test_cases.extend([{
                "title": f"Form {i + 1} Validation",
                "category": "functional",
                "priority": "high",
                "preconditions": f"Form {i + 1} is present and accessible on the page",
                "steps": [
                    {
                        "action": "fill",
                        "field": "form",
                        "description": "Fill form fields with valid data"
                    },
                    {
                        "action": "submit",
                        "field": "form",
                        "description": "Submit form"
                    }
                ],
                "expectedResults": {
                    "type": "success",
                    "details": {
                        "message": "Form submitted successfully"
                    }
                },
                "edgeCases": ["Invalid form data", "Form submission timeout", "Network error during submission"]
            } for i, _ in enumerate(page_elements['forms'])])

        # Generate POM code
        # Helper functions for POM code generation
        def generate_element_getters(elements):
            getters = []

            if elements['navigation']:
                getters.append(
                    "    async getNavigation() {\n        return this.page.locator('nav');\n    }")

            if elements['links']:
                getters.append(
                    "    async getLinks() {\n        return this.page.locator('a');\n    }")

            if elements['buttons']:
                getters.append(
                    "    async getButtons() {\n        return this.page.locator('button, input[type=\"button\"], input[type=\"submit\"]');\n    }")

            if elements['images']:
                getters.append(
                    "    async getImages() {\n        return this.page.locator('img');\n    }")

            if elements['headings']:
                getters.append(
                    "    async getHeadings() {\n        return this.page.locator('h1, h2, h3, h4, h5, h6');\n    }")

            if elements['forms']:
                getters.append(
                    "    async getForms() {\n        return this.page.locator('form');\n    }")

            return "\n\n".join(getters)

        def generate_element_actions(elements):
            actions = []

            if elements['navigation']:
                actions.append("""    async navigateToLink(href: string) {
        await this.page.click(`nav a[href="${href}"]`);
    }""")

            if elements['links']:
                actions.append("""    async clickLink(text: string) {
        await this.page.click(`a:text("${text}")`);
    }""")

            if elements['buttons']:
                actions.append("""    async clickButton(text: string) {
        await this.page.click(`button:text("${text}"), input[type="button"][value="${text}"], input[type="submit"][value="${text}"]`);
    }""")

            if elements['forms']:
                actions.append("""    async fillForm(formIndex: number, data: Record<string, string>) {
        const form = await this.page.locator('form').nth(formIndex);
        for (const [name, value] of Object.entries(data)) {
            await form.locator(`[name="${name}"]`).fill(value);
        }
    }
    
    async submitForm(formIndex: number) {
        const form = await this.page.locator('form').nth(formIndex);
        await form.evaluate(f => f.submit());
    }""")

            return "\n\n".join(actions)

        def generate_element_assertions(elements):
            assertions = []

            if elements['navigation']:
                assertions.append("""    async assertNavigationVisible() {
        await expect(this.page.locator('nav')).toBeVisible();
    }""")

            if elements['links']:
                assertions.append("""    async assertLinkExists(text: string) {
        await expect(this.page.locator(`a:text("${text}")`)).toBeVisible();
    }""")

            if elements['images']:
                assertions.append("""    async assertImagesHaveAlt() {
        const images = await this.page.locator('img').all();
        for (const image of images) {
            await expect(image).toHaveAttribute('alt');
        }
    }""")

            if elements['forms']:
                assertions.append("""    async assertFormExists(index: number) {
        await expect(this.page.locator('form').nth(index)).toBeVisible();
    }""")

            return "\n\n".join(assertions)

        # Generate POM code
        pom_code = f"""
import {{ Page, Locator, expect }} from '@playwright/test';

export class {url.split('/')[-2].capitalize() if url.split('/')[-2] else 'Home'}Page {{
    readonly page: Page;
    
    constructor(page: Page) {{
        this.page = page;
    }}

    // Navigation
    async goto() {{
        await this.page.goto('{url}');
    }}

    // Getters for elements
{generate_element_getters(page_elements)}

    // Actions
{generate_element_actions(page_elements)}

    // Assertions
{generate_element_assertions(page_elements)}
}}
"""

        result = {
            "testCases": test_cases,
            "pomCode": pom_code,
            "metadata": {
                "url": url,
                "timestamp": os.getenv('CURRENT_TIME', ''),
                "elementCounts": {
                    "links": len(page_elements['links']),
                    "buttons": len(page_elements['buttons']),
                    "images": len(page_elements['images']),
                    "headings": len(page_elements['headings']),
                    "forms": len(page_elements['forms'])
                }
            }
        }

        # Cache successful result
        if use_cache:
            cache_result(cache_key, result)
        return result

    except ValueError as e:
        logger.error(f"Validation error for {url}: {e}")
        return {"error": f"Validation error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error analyzing page {url}: {e}")
        return {
            "error": "Analysis error",
            "details": str(e),
            "timestamp": os.getenv('CURRENT_TIME', '')
        }


if __name__ == "__main__":
    # Example usage for testing
    sample_html = """
    <form action="/login" method="POST">
        <input type="text" id="username" name="username">
        <input type="password" id="password" name="password">
        <input type="submit" id="submit">
    </form>
    """
    result = analyze_page(sample_html, "https://example.com/login")
    print(json.dumps(result, indent=2))
