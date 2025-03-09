# Generator Component Documentation

## Overview

The generator component is responsible for creating automated test cases in TypeScript for Playwright. It converts structured test case definitions into executable test code, along with supporting documentation in JSON and Markdown formats.

## Key Features

- TypeScript test code generation for Playwright
- Page Object Model (POM) integration
- Multiple output formats (TypeScript, JSON, Markdown)
- Support for various test actions (fill, click, assert)
- Automated test case documentation
- Edge case tracking

## Core Functions

### generate_test_code

```python
def generate_test_code(test_cases: list, pom_code: str, page_url: str) -> str
```

#### Parameters

- `test_cases` (list): Collection of test case dictionaries
- `pom_code` (str): Page Object Model class implementation
- `page_url` (str): Target page URL

#### Returns

- `str`: Generated TypeScript test code

#### Functionality

1. Extracts class name from URL
2. Imports Playwright test dependencies
3. Integrates POM class code
4. Generates test cases with:
   - Test title and description
   - Page object initialization
   - Test steps implementation
   - Assertions and validations

### generate_outputs

```python
def generate_outputs(test_cases: list, output_dir: str)
```

#### Parameters

- `test_cases` (list): Collection of test case dictionaries
- `output_dir` (str): Directory for output files

#### Functionality

1. Creates output directory if needed
2. Generates JSON output:
   - Structured test case data
   - Machine-readable format
3. Generates Markdown output:
   - Tabular test case documentation
   - Human-readable format

## Test Case Structure

### Test Case Dictionary Format

```python
{
    "title": str,           # Test case title
    "preconditions": str,   # Required setup/conditions
    "steps": [              # List of test steps
        {
            "action": str,  # "fill", "click", or "assert"
            "field": str,   # Target element/field
            "value": str    # (Optional) Input value
        }
    ],
    "expectedResults": {    # Expected outcome
        "type": str,       # "redirect" or "elementVisible"
        "url": str,        # For redirect type
        "selector": str    # For elementVisible type
    },
    "edgeCases": [str]     # List of edge cases to consider
}
```

## Output Formats

### TypeScript Test Code

```typescript
import { test, expect } from '@playwright/test';

// Page Object Model class
class PageName {
  constructor(page) {
    this.page = page;
  }
  // POM methods
}

test('Test case title', async ({ page }) => {
  const pageObject = new PageName(page);
  await pageObject.goto('url');
  // Test steps
  // Assertions
});
```

### JSON Output

```json
{
  "testCases": [
    {
      "title": "Test case title",
      "preconditions": "Setup requirements",
      "steps": [],
      "expectedResults": {},
      "edgeCases": []
    }
  ]
}
```

### Markdown Output

| Title      | Preconditions | Steps        | Expected Results | Edge Cases |
| ---------- | ------------- | ------------ | ---------------- | ---------- |
| Test Title | Setup         | Action Steps | Expected Outcome | Edge Cases |

## Usage Example

```python
test_cases = [{
    "title": "Verify successful login",
    "preconditions": "User is on the login page",
    "steps": [
        {"action": "fill", "field": "username", "value": "valid_user"},
        {"action": "fill", "field": "password", "value": "valid_password"},
        {"action": "click", "field": "submit"}
    ],
    "expectedResults": {"type": "redirect", "url": "/dashboard"},
    "edgeCases": ["Invalid username", "Invalid password"]
}]

pom_code = """
class LoginPage {
    constructor(page) {
        this.page = page;
    }
    async navigate(url) { await this.page.goto(url); }
    async fillUsername(value) { await this.page.locator('#username').fill(value); }
    async fillPassword(value) { await this.page.locator('#password').fill(value); }
    async clickSubmit() { await this.page.locator('#submit').click(); }
}
"""

# Generate test code
test_code = generate_test_code(test_cases, pom_code, "https://example.com/login")

# Generate documentation
generate_outputs(test_cases, "outputs/test")
```

## Best Practices

1. **Test Case Design**

   - Use descriptive test titles
   - Include clear preconditions
   - Break down steps atomically
   - Specify concrete expected results
   - Document relevant edge cases

2. **Page Object Model**

   - Create reusable page methods
   - Use meaningful method names
   - Implement proper element selectors
   - Handle async operations correctly

3. **Output Management**
   - Use consistent output directories
   - Version control test artifacts
   - Review generated documentation
   - Validate test code syntax

## Limitations

- Fixed action types (fill, click, assert)
- Basic assertion support
- Single page object per test
- Limited edge case implementation

## Future Enhancements

1. Additional action types
2. Complex assertion support
3. Multi-page test scenarios
4. Custom test templates
5. Extended edge case handling
6. Test data management
7. Conditional test steps
8. Parameterized tests

## Dependencies

- `os`: File system operations
- `json`: JSON data handling
- Playwright test framework
- TypeScript runtime
