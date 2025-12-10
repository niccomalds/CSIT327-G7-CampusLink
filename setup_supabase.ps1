# Quick setup script for Supabase storage implementation (Windows)

Write-Host "🚀 Setting up Supabase Storage for CampusLink..." -ForegroundColor Green
Write-Host ""

# Step 1: Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Step 2: Run migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Yellow
python manage.py migrate

# Step 3: Check Supabase configuration
Write-Host "🔍 Checking Supabase configuration..." -ForegroundColor Yellow
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

Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. In Supabase dashboard, create a bucket named 'applications'"
Write-Host "2. Set the bucket to Private (only authenticated users)"
Write-Host "3. Configure RLS policies for secure file access"
Write-Host "4. Test by uploading a resume in the student dashboard"
Write-Host ""
