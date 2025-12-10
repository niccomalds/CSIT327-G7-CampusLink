#!/bin/bash
# Quick setup script for Supabase storage implementation

echo "🚀 Setting up Supabase Storage for CampusLink..."

# Step 1: Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Step 2: Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Step 3: Check Supabase configuration
echo "🔍 Checking Supabase configuration..."
python -c "
from MyLogin.supabase_client import supabase
try:
    # Test connection
    response = supabase.auth.get_session()
    print('✅ Supabase connection successful!')
except Exception as e:
    print(f'❌ Supabase connection failed: {e}')
    print('Please ensure SUPABASE_URL and SUPABASE_KEY are set in .env')
"

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. In Supabase dashboard, create a bucket named 'applications'"
echo "2. Set the bucket to Private (only authenticated users)"
echo "3. Configure RLS policies for secure file access"
echo "4. Test by uploading a resume in the student dashboard"
echo ""
