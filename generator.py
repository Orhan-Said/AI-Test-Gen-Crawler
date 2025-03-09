import os
import json


def generate_test_code(test_cases, pom_code, page_url):
    """
    Generate TypeScript test code for Playwright.

    Args:
        test_cases (list): List of test case dictionaries.
        pom_code (str): POM class code from LLM.
        page_url (str): The page URL.

    Returns:
        str: Generated TypeScript test code.
    """
    class_name = page_url.split(
        '/')[-1].capitalize() + 'Page' if page_url.split('/')[-1] else 'HomePage'
    test_code = f"import {{ test, expect }} from '@playwright/test';\n\n{pom_code}\n\n"
    for tc in test_cases:
        test_code += f"test('{tc['title']}', async ({{ page }}) => {{\n"
        test_code += f"  const pageObject = new {class_name}(page);\n"
        test_code += f"  // {tc['preconditions']}\n"
        test_code += f"  await pageObject.goto('{page_url}');\n"
        for step in tc['steps']:
            if step['action'] == 'fill':
                field = step['field'].capitalize()
                test_code += f"  await pageObject.fill{field}('{step['value']}');\n"
            elif step['action'] == 'click':
                field = step['field'].capitalize()
                test_code += f"  await pageObject.click{field}();\n"
            elif step['action'] == 'assert':
                field = step['field'].capitalize()
                test_code += f"  await pageObject.assert{field}Exists();\n"
        if tc['expectedResults']['type'] == 'redirect':
            test_code += f"  await expect(page).toHaveURL('{tc['expectedResults']['url']}');\n"
        elif tc['expectedResults']['type'] == 'elementVisible':
            selector = tc['expectedResults']['selector'].replace('.', '')
            test_code += f"  await expect(pageObject.get{selector}()).toBeVisible();\n"
        test_code += "});\n\n"
    return test_code


def generate_outputs(test_cases, output_dir):
    """
    Generate JSON and Markdown outputs for test cases.

    Args:
        test_cases (list): List of test case dictionaries.
        output_dir (str): Directory to save output files.
    """
    os.makedirs(output_dir, exist_ok=True)

    # JSON output
    with open(f"{output_dir}/test_cases.json", 'w') as f:
        json.dump({"testCases": test_cases}, f, indent=2)

    # Markdown output
    md_content = "| Title | Preconditions | Steps | Expected Results | Edge Cases |\n"
    md_content += "|-------|---------------|-------|------------------|------------|\n"
    for tc in test_cases:
        steps = "; ".join([f"{s['action']} {s['field']}" +
                          (f" with '{s['value']}'" if 'value' in s else "") for s in tc['steps']])
        exp_res = f"{tc['expectedResults']['type']} ({tc['expectedResults'].get('url', tc['expectedResults'].get('selector'))})"
        edge_cases = "; ".join(tc['edgeCases'])
        md_content += f"| {tc['title']} | {tc['preconditions']} | {steps} | {exp_res} | {edge_cases} |\n"
    with open(f"{output_dir}/test_cases.md", 'w') as f:
        f.write(md_content)


if __name__ == "__main__":
    # Example usage for testing
    sample_test_cases = [
        {
            "title": "Verify successful login",
            "preconditions": "User is on the login page",
            "steps": [
                {"action": "fill", "field": "username", "value": "valid_user"},
                {"action": "fill", "field": "password", "value": "valid_password"},
                {"action": "click", "field": "submit"}
            ],
            "expectedResults": {"type": "redirect", "url": "/dashboard"},
            "edgeCases": ["Invalid username", "Invalid password"]
        }
    ]
    sample_pom = """
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
    test_code = generate_test_code(
        sample_test_cases, sample_pom, "https://example.com/login")
    print(test_code)
    generate_outputs(sample_test_cases, "outputs/test")
