
from dotenv import load_dotenv
from supabase import create_client
import os
load_dotenv()


class SupabaseClient:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        # Validate environment variables
        if not all([supabase_url, supabase_key]):
            raise ValueError(
                "Supabase configuration is incomplete. Check SUPABASE_URL and SUPABASE_KEY.")
        self.supabase = create_client(supabase_url, supabase_key)

    def isCrawled(self, url):
        try:
            result = self.supabase.table(
                'pages').select().eq('url', url).execute()
            return len(result) > 0
        except Exception as e:
            print(f"Error checking if {url} is crawled: {e}")

    def insert_page_to_db(self, url, html, title, origin):
        try:
            print(f"Storing {url} in Supabase")
            self.supabase.table('pages').insert({
                'url': url,
                'html': html,
                'title': title,
                'origin_id': origin
            }).execute()
            print("added to supabase")
        except Exception as e:
            print(f"Error storing {url} in Supabase: {e}")
            return None

    def get_page_from_db(self, url):
        try:
            print(f"Retrieving {url} from Supabase")
            result = self.supabase.table(
                'pages').select().eq('url', url).execute()
            return result.data[0]
        except Exception as e:
            print(f"Error retrieving {url} from Supabase: {e}")
            return None

    def get_page_urls_by_origin(self, origin_id):
        try:
            print(f"Retrieving pages from origin {origin_id} from Supabase")
            result = self.supabase.table(
                'pages').select().eq('origin_id', origin_id).execute()
            return result
        except Exception as e:
            print(
                f"Error retrieving pages from origin {origin_id} from Supabase: {e}")
            return None
