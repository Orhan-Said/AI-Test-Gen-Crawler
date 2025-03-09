import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from urllib.parse import urlparse
from utils.SupabaseClient import SupabaseClient
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()


async def crawl_website(start_url):
    supabase = SupabaseClient()
    origin = str(uuid4())
    """
    Crawl a website starting from start_url and store data in Supabase.

    Args:
        start_url (str): The starting URL to crawl.

    Returns:
        list: List of crawled page URLs.
    """
    visited = set()
    to_crawl = [start_url]
    crawled_pages = []
    browser_config = BrowserConfig(browser_type="chromium",
                                   headless=False,
                                   use_managed_browser=False,
                                   cdp_url=None,
                                   use_persistent_context=False,
                                   user_data_dir=None,
                                   chrome_channel="chromium",
                                   channel="chromium",
                                   proxy=None,
                                   proxy_config=None,
                                   viewport_width=1080,
                                   viewport_height=600,
                                   accept_downloads=False,
                                   downloads_path=None,
                                   storage_state=None,
                                   ignore_https_errors=True,
                                   java_script_enabled=True,
                                   sleep_on_close=False,
                                   verbose=True,
                                   cookies=None,
                                   headers=None,
                                   user_agent="Mozilla/5.0 (X11; Linux x86_64) ",
                                   user_agent_mode="",
                                   user_agent_generator_config={},
                                   text_mode=False,
                                   light_mode=False,
                                   extra_args=None,
                                   debugging_port=9222,
                                   host="localhost")
    run_config = CrawlerRunConfig(
        magic=True,
        simulate_user=True,
        override_navigator=True,
        verbose=True,
        cache_mode=CacheMode.ENABLED,
        check_robots_txt=True,
    )

    visited = set()
    async with AsyncWebCrawler(config=browser_config) as crawler:

        while to_crawl:
            url = to_crawl.pop(0)
            if url in visited:
                continue
            visited.add(url)
            if supabase.isCrawled(url=url):
                print(f"{url} is already crawled")
                continue
            try:
                print(f"Crawling {url}")
                result = await crawler.arun(url=url, config=run_config)
                if result.success:
                    html = result.html
                    title = result.metadata["title"]
                    # Store in Supabase

                    print(f"Storing {url} in Supabase")
                    supabase.insert_page_to_db(
                        url=url, html=html, title=title, origin=origin)

                    crawled_pages.append(url)

                    # Extract and filter links within the same domain
                    links = result.links['internal']
                    print(
                        f"Extracted {len(links)} links from {url}")

                    domain = urlparse(start_url).netloc
                    for link in links:
                        href = link['href']
                        print(f"Checking {href}")
                        if urlparse(href).netloc == domain and href not in visited:
                            print(f"Adding {href} to crawl queue")
                            to_crawl.append(href)
            except Exception as e:
                print(f"Error crawling {url}: {e}")
    return crawled_pages

if __name__ == "__main__":
    # Example usage
    asyncio.run(crawl_website(""))
