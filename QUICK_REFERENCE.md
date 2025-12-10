# Quick Reference - Supabase Storage Implementation

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
python manage.py migrate
```

### 2. Configure Supabase
- Create bucket `applications` in Supabase
- Set to `Private`
- Apply RLS policies (see SUPABASE_RLS_POLICIES.md)

### 3. Test
- Student applies → Resume uploaded to Supabase
- Organization views → Gets signed URL
- Organization downloads → Works via URL

---

## 📁 File Changes

### New Files
- `MyLogin/supabase_storage.py` - Storage utility class
- `Myapp/migrations/0011_add_supabase_storage_fields.py` - Database migration
- Documentation files:
  - `SUPABASE_STORAGE_IMPLEMENTATION.md`
  - `SUPABASE_RLS_POLICIES.md`
  - `IMPLEMENTATION_SUMMARY.md`
- Setup scripts:
  - `setup_supabase.sh` (Linux/Mac)
  - `setup_supabase.ps1` (Windows)

### Modified Files
- `Myapp/models.py` - Added Supabase fields + get_resume_url()
- `MyLogin/views.py` - Updated 3 views, added download_resume
- `MyLogin/urls.py` - Added download route
- `requirements.txt` - Added supabase>=2.4.0

---

## 🔑 Key Methods

### Application Model
```python
# In your views or templates
app = Application.objects.get(id=1)
url = app.get_resume_url()  # Auto-handles Supabase or local

# Returns:
# - Supabase signed URL (valid 7 days) if using Supabase
# - Local file URL if fallback
# - None if no file
```

### SupabaseStorageManager
```python
from MyLogin.supabase_storage import SupabaseStorageManager

# Upload
result = SupabaseStorageManager.upload_resume(file_obj, student_id, app_id)
# Returns: {'success': bool, 'path': str, 'error': str}

# Get signed URL
url = SupabaseStorageManager.get_signed_url(file_path)
# Returns: str (signed URL) or None

# Delete file
result = SupabaseStorageManager.delete_file(file_path)
# Returns: {'success': bool, 'error': str}

# Check existence
exists = SupabaseStorageManager.file_exists(file_path)
# Returns: bool

# Download file
content = SupabaseStorageManager.download_file(file_path)
# Returns: bytes or None
```

---

## 📊 Data Structure

### File Path Format
```
applications/resumes/{student_id}/{application_id}.{extension}

Example:
applications/resumes/42/123.pdf
```

### Application Model Fields
```python
class Application(models.Model):
    # ... existing fields ...
    
    # New Supabase fields:
    resume_supabase_path = CharField()      # Path in bucket
    resume_signed_url = TextField()         # Cached URL
    signed_url_expires_at = DateTimeField() # Expiry time
    uses_supabase_storage = BooleanField()  # Flag
```

---

## 🔐 Security

### Access Control
```python
# Only these can access:
1. Student who uploaded the file
2. Organization reviewing the application
3. (Future) Admin with override

# Enforced in:
- download_resume view (Django)
- RLS policies (Supabase)
- Signed URL expiration (7 days)
```

### Bucket Privacy
- Bucket: `Private` (requires authentication)
- RLS Policies: Enable all 4 policies (see guide)
- Signed URLs: Auto-expire after 7 days

---

## ⚙️ Configuration

### Environment Variables
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key
```

### Django Settings
No changes needed to `settings.py`

### Database
Run migration to add fields:
```bash
python manage.py migrate
```

---

## 🧪 Testing

### Manual Test Flow
1. **Upload**
   - Go to student dashboard
   - Apply for opportunity
   - Upload resume
   - Check Supabase bucket for file

2. **Access**
   - Go to organization dashboard
   - View applicants
   - Click "Download Resume"
   - Should work with signed URL

3. **Security**
   - Try accessing URL as different user → Should fail
   - Wait past 7 days → Should auto-regenerate
   - Check local fallback by disabling Supabase

---

## 🐛 Troubleshooting

### Upload Fails
```python
# Check error in console:
# "Supabase upload error: ..."

# Solutions:
1. Verify SUPABASE_URL and SUPABASE_KEY in .env
2. Check bucket "applications" exists
3. Check bucket is "Private"
4. Verify RLS policies are enabled
```

### Download Fails
```python
# Check error response:
# "Access denied" → User not authorized
# "Resume file not found" → File not in bucket
# "Application not found" → Wrong app ID

# Solutions:
1. Verify user has access to application
2. Check file exists in Supabase
3. Check RLS policies allow access
4. Verify signed URL not expired (should auto-refresh)
```

### URL Expires
- Automatic refresh on `get_resume_url()` call
- Cached for 7 days
- No user action needed

---

## 📈 Monitoring

### Check Upload Success
```python
# In Django shell:
from Myapp.models import Application
app = Application.objects.latest('id')
print(app.uses_supabase_storage)  # Should be True
print(app.resume_supabase_path)   # Should show path
print(app.resume_signed_url)      # Should show URL
```

### Monitor Supabase
1. Go to Supabase dashboard
2. Storage → applications bucket
3. See uploaded files
4. Monitor storage usage
5. Check API requests

### Logs
```bash
# Development
python manage.py runserver

# Check console for:
# "Supabase upload error: ..." (if any)
# Application successfully uploaded logs
```

---

## 🎯 Features

✅ Cloud-based file storage  
✅ Secure signed URLs (7-day expiry)  
✅ Access control (student/org only)  
✅ Backward compatible (local fallback)  
✅ Automatic URL refresh  
✅ URL caching (reduced API calls)  
✅ Error handling (non-blocking uploads)  
✅ Cross-user file access  

---

## 📚 More Info

- **Implementation Details**: See `SUPABASE_STORAGE_IMPLEMENTATION.md`
- **Security Policies**: See `SUPABASE_RLS_POLICIES.md`
- **All Changes**: See `IMPLEMENTATION_SUMMARY.md`

---

## 🔗 Useful Links

- [Supabase Docs](https://supabase.com/docs)
- [Storage Guide](https://supabase.com/docs/guides/storage)
- [RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Python SDK](https://github.com/supabase/supabase-py)

---

## ❓ FAQ

**Q: What if Supabase is down?**  
A: Application falls back to local file. Uploads still work locally.

**Q: Can students delete their files?**  
A: Yes, via RLS policy. Download_resume view doesn't support delete yet.

**Q: How many files can we store?**  
A: Unlimited (limited by Supabase plan).

**Q: What file types are supported?**  
A: PDF, DOC, DOCX (configurable in code).

**Q: Can organizations see each other's applicants?**  
A: No, RLS policies restrict to their own postings.

**Q: How do I migrate existing files?**  
A: See "Migration from Local to Cloud" in IMPLEMENTATION_SUMMARY.md

---

Last Updated: 2025-12-10
