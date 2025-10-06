from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Kuha sa Supabase URL ug Key
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
