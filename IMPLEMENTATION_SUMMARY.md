# Supabase Storage Implementation - Summary of Changes

## Overview
Implemented Supabase bucket storage for application files to allow organizations to view student-uploaded resumes. This solves the issue where files were only accessible locally.

## Files Modified

### 1. **MyLogin/supabase_storage.py** (NEW)
- Complete storage management utility class
- Methods:
  - `upload_resume()` - Upload file to Supabase bucket
  - `get_signed_url()` - Generate 7-day expiring signed URLs
  - `delete_file()` - Remove files from bucket
  - `file_exists()` - Check file existence
  - `download_file()` - Download file content
- Bucket: `applications`
- Path structure: `resumes/{student_id}/{application_id}.{extension}`

### 2. **Myapp/models.py** (UPDATED)
Added fields to `Application` model:
```python
resume_supabase_path = CharField(max_length=500)  # Path in Supabase bucket
resume_signed_url = TextField()                    # Cached signed URL
signed_url_expires_at = DateTimeField()           # URL expiration timestamp
uses_supabase_storage = BooleanField(default=False)  # Flag for storage type

# New method:
def get_resume_url()  # Returns Supabase URL or local file URL
```

### 3. **Myapp/migrations/0011_add_supabase_storage_fields.py** (NEW)
Migration to add the 4 new fields to Application model

### 4. **MyLogin/views.py** (UPDATED)
- Added `from io import BytesIO` import
- **student_dashboard view**: Now uploads resume to Supabase after application creation
- **create_application view**: Now uploads resume to Supabase after application creation
- **get_application_details view**: Updated to use `application.get_resume_url()` instead of `application.resume.url`
- **download_resume view** (NEW): Secure file download with access control
  - Only student or reviewing organization can download
  - Returns file from Supabase or local fallback
  - Proper error handling and access checks

### 5. **MyLogin/urls.py** (UPDATED)
Added new URL route:
```python
path('download-resume/<int:application_id>/', views.download_resume, name='download_resume')
```

### 6. **requirements.txt** (UPDATED)
Added dependency:
```
supabase>=2.4.0
```

## Key Features

### ✅ Cloud Storage
- Files stored in Supabase buckets, not local server
- Scalable and reliable cloud infrastructure

### ✅ Secure Access
- Signed URLs expire after 7 days
- Access control: only student and organization can download
- Private bucket requires authentication

### ✅ Backward Compatibility
- Falls back to local files if Supabase upload fails
- Existing applications continue to work
- Graceful degradation if Supabase unavailable

### ✅ URL Caching
- Signed URLs cached to reduce API calls
- Automatic refresh when expired
- Efficient database queries

### ✅ Error Handling
- Non-blocking uploads (async)
- Application creation succeeds even if upload fails
- Detailed error logging

## How to Use

### 1. Install & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run setup script (Windows)
.\setup_supabase.ps1

# Or (Linux/Mac)
bash setup_supabase.sh
```

### 2. Configure Supabase
1. Create bucket named `applications` in Supabase dashboard
2. Set bucket to `Private`
3. Apply RLS policies (see SUPABASE_RLS_POLICIES.md)

### 3. Test
1. Student applies for opportunity → Resume uploaded to Supabase
2. Organization views applicant → Gets Supabase signed URL
3. Organization downloads resume → Works via signed URL

## Architecture

```
Student Upload Flow:
┌─────────────────┐
│ Student applies │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Create Application      │ (with local FileField)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Upload to Supabase      │ (async, non-blocking)
│ in background           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Update Application      │
│ with Supabase info      │
└─────────────────────────┘

Organization Download Flow:
┌──────────────────────┐
│ View Applicant       │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────────────┐
│ get_application_details()    │
└─────────┬────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ Application.get_resume_url() │
│ (validates access, checks    │
│  URL expiry)                 │
└─────────┬────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ Return Supabase Signed URL   │
│ or Local File URL            │
└──────────────────────────────┘
```

## Security Model

### Authentication
- All Supabase operations require SUPABASE_KEY authentication
- RLS policies enforce row-level access control
- Signed URLs have 7-day expiration

### Authorization
- Students can only upload to their own folder (`resumes/{student_id}/`)
- Students can only download their own files
- Organizations can only download files from their own postings
- Admins can configure and manage buckets

### Data Flow
```
Client → Django View → SupabaseStorageManager → Supabase API → Supabase Storage
                ↓
            Access Control Check
            (Student/Organization verification)
                ↓
            Generate/Validate Signed URL
                ↓
            Return URL or File Content
```

## Performance Considerations

### Optimizations
- Signed URLs cached (default 7 days)
- Minimal API calls via caching
- Non-blocking uploads (don't wait for completion)
- Lazy URL generation on first access

### Scalability
- Cloud storage handles unlimited files
- Database only stores path references
- Supabase handles concurrent access
- Automatic CDN distribution

## Migration from Local to Cloud

For existing applications:
```python
from MyLogin.supabase_storage import SupabaseStorageManager
from Myapp.models import Application

for app in Application.objects.filter(uses_supabase_storage=False):
    if app.resume:
        result = SupabaseStorageManager.upload_resume(
            app.resume, 
            student_id=app.student.id,
            application_id=app.id
        )
        if result['success']:
            app.resume_supabase_path = result['path']
            app.uses_supabase_storage = True
            # Generate signed URL...
            app.save()
```

## Testing Checklist

- [ ] Student can upload resume via modal
- [ ] Student can upload resume via create_application form
- [ ] File appears in Supabase bucket with correct path
- [ ] Application stored with Supabase info
- [ ] Organization can view applicant details
- [ ] Resume URL is a Supabase signed URL
- [ ] Organization can download resume
- [ ] Access denied for unauthorized users
- [ ] Signed URL works in browser
- [ ] URL regenerates after 7 days

## Troubleshooting

See SUPABASE_STORAGE_IMPLEMENTATION.md for detailed troubleshooting guide

Common issues:
1. "Supabase upload error" → Check credentials in .env
2. "Access denied on download" → Check RLS policies and access control
3. "Resume not found" → Check file path in bucket
4. "Signed URL expired" → Should auto-regenerate, check get_resume_url() method

## Documentation Files

1. **SUPABASE_STORAGE_IMPLEMENTATION.md** - Complete implementation guide
2. **SUPABASE_RLS_POLICIES.md** - Security policies and configuration
3. **setup_supabase.sh** - Linux/Mac setup script
4. **setup_supabase.ps1** - Windows setup script

## Next Steps

1. Run migrations: `python manage.py migrate`
2. Configure Supabase bucket and RLS policies
3. Update .env with SUPABASE_URL and SUPABASE_KEY
4. Test the entire flow (upload, access, download)
5. Monitor Supabase storage usage in dashboard
6. Consider implementing additional features (multiple files, preview, etc.)

## Questions or Issues?

1. Check the troubleshooting section in SUPABASE_STORAGE_IMPLEMENTATION.md
2. Review SUPABASE_RLS_POLICIES.md for security configuration
3. Check application logs: `python manage.py runserver`
4. Verify Supabase dashboard for bucket status and logs
