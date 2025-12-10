from supabase import create_client, Client
import os
from dotenv import load_dotenv
from decouple import config
import logging

# Load .env file
load_dotenv()

# Get Supabase credentials from .env or decouple
SUPABASE_URL = config("SUPABASE_URL", default=os.getenv("SUPABASE_URL"))
SUPABASE_KEY = config("SUPABASE_KEY", default=os.getenv("SUPABASE_KEY"))

# Initialize supabase client only if credentials are present. Do not raise on import,
# because imports occur during build/deploy and missing env vars should not crash the app.
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logging.warning(f"Failed to initialize Supabase client: {e}")
        supabase = None
else:
    # Credentials not provided; warn but don't crash
    logging.info("SUPABASE_URL or SUPABASE_KEY not set - Supabase client disabled.")
