import asyncio
import os
from dotenv import load_dotenv
from analyzer import analyze_page
from utils.SupabaseClient import SupabaseClient
from crawler import crawl_website
from generator import generate_outputs, generate_test_code
from qa_validator import validate_test_cases
from repo_integrator import integrate_with_repo

load_dotenv()
REPO_URL = os.getenv("REPO_URL")


async def process_website(start_url):
    supabase = SupabaseClient()
    """
    Process a website from crawling to repository integration.

    Args:
        start_url (str): The starting URL to process.
    """

    # Step 1: Crawl the website
    print(f"Starting crawl for {start_url}")
    crawled_urls = await crawl_website(start_url)
    if not crawled_urls:
        print("No URLs were crawled, checking db for existing data.")
        query_result = supabase.get_page_from_db(start_url)
        if not query_result:
            print("No data found in db.")
            return
        print("Data found in db.")
        crawled_urls = supabase.get_page_urls_by_origin(
            query_result['origin_id'])

    # Step 2: Analyze each page and generate test cases
    files_to_add = {}
    output_dir = f"outputs/{start_url.replace('https://', '').replace('/', '_')}"
    os.makedirs(output_dir, exist_ok=True)
    print(crawled_urls)
    for url in crawled_urls:
        try:
            # Safely query Supabase
            query_result = supabase.get_page_from_db(url)

            # if not query_result.get('data'):
            #     print(f"No data found for URL: {url}")
            #     continue

            if not query_result.get('html'):
                print(f"No HTML content found for URL: {url}")
                continue

            analysis_result = analyze_page(query_result.get('html'), url)
            if not analysis_result:
                print(f"Analysis failed for URL: {url}")
                continue

            # Extract required data
            if isinstance(analysis_result, dict) and 'error' in analysis_result:
                print(
                    f"Analysis error for URL {url}: {analysis_result['error']}")
                continue

            test_cases = analysis_result.get('testCases', [])
            pom_code = analysis_result.get('pomCode', '')

            if not test_cases or not pom_code:
                print(f"Invalid analysis result format for URL: {url}")
                continue

            # Ensure each test case has required fields
            for tc in test_cases:
                if 'preconditions' not in tc:
                    tc['preconditions'] = 'No specific preconditions'
                if 'edgeCases' not in tc:
                    tc['edgeCases'] = []

            # Step 3: Generate test code
            # Create safe path by replacing slashes with underscores
            page_path = url.replace(start_url, '').strip('/')
            if not page_path:
                page_path = 'home'
            safe_path = page_path.replace('/', '_')

            test_code = generate_test_code(test_cases, pom_code, url)
            if not test_code:
                print(f"Failed to generate test code for URL: {url}")
                continue

            # Step 4: Validate test cases
            try:
                validation_feedback = validate_test_cases(test_cases, pom_code)
                validation_dir = os.path.dirname(
                    f"{output_dir}/validation_feedback_{safe_path}.txt")
                os.makedirs(validation_dir, exist_ok=True)
                validation_path = f"{output_dir}/validation_feedback_{safe_path}.txt"
                with open(validation_path, 'w') as f:
                    f.write(
                        validation_feedback or "Validation produced no feedback")
            except Exception as e:
                print(f"Error during validation for {url}: {e}")
                continue

            # Step 5: Prepare files for repository
            pom_file = f"pages/{page_path}.page.ts"
            test_file = f"tests/{page_path}.test.ts"
            files_to_add[pom_file] = pom_code
            files_to_add[test_file] = test_code

            # Step 6: Generate JSON and Markdown outputs
            try:
                generate_outputs(test_cases, output_dir)
            except Exception as e:
                print(f"Error generating outputs for {url}: {e}")
                continue

        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            continue

    if not files_to_add:
        print("No files were generated. Check the logs for errors.")
        return

    # Step 7: Integrate with repository
    try:
        integrate_with_repo(REPO_URL, files_to_add)
        print(f"Processing completed for {start_url}")
    except Exception as e:
        print(f"Error integrating with repository: {e}")

if __name__ == "__main__":
    url = "https://www.orhansaid.com/"
    asyncio.run(process_website(url))
