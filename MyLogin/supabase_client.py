from supabase import create_client
import os
from dotenv import load_dotenv

# i-load ang .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
