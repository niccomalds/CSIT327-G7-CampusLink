# Supabase Storage Implementation Guide

## Overview
This document describes the implementation of Supabase bucket storage for application files (resumes) in CampusLink. This allows organizations to securely view files uploaded by students, addressing the issue where uploaded files were only accessible locally.

## What Was Implemented

### 1. **New Files Created**
- `MyLogin/supabase_storage.py` - Storage management utility class with methods for uploading, downloading, and generating signed URLs

### 2. **Database Changes**
- New migration: `Myapp/migrations/0011_add_supabase_storage_fields.py`
- Added fields to `Application` model:
  - `resume_supabase_path` - Path to the resume file in Supabase bucket
  - `resume_signed_url` - Cached signed URL for secure file access
  - `signed_url_expires_at` - Timestamp when the signed URL expires
  - `uses_supabase_storage` - Boolean flag to track if file is in Supabase

### 3. **Model Enhancements**
- Added `get_resume_url()` method to `Application` model that:
  - Checks if signed URL is still valid (if using Supabase)
  - Generates a new signed URL if expired
  - Falls back to local file URL for backward compatibility

### 4. **View Updates**
- **`student_dashboard`** - Now uploads resume to Supabase when application is submitted via modal
- **`create_application`** - Now uploads resume to Supabase when application is created
- **`get_application_details`** - Updated to use `get_resume_url()` method that serves Supabase signed URLs
- **`download_resume`** (NEW) - New view for secure file downloads with access control

### 5. **URL Routing**
- Added new route: `/download-resume/<application_id>/` for downloading files

### 6. **Dependencies**
- Added `supabase>=2.4.0` to requirements.txt

## How It Works

### File Upload Flow
1. Student submits application with resume file
2. Application is created with local file storage (Django FileField)
3. File is uploaded to Supabase bucket asynchronously
4. Application fields are updated with Supabase path and signed URL
5. If upload fails, application still works with local file (fallback)

### File Access Flow
1. Organization views applicant details
2. `get_application_details()` returns resume URL via `get_resume_url()`
3. If using Supabase and URL is valid → returns cached signed URL
4. If using Supabase and URL expired → generates new signed URL and caches it
5. If local file → returns local file URL
6. Organization can download via signed URL (7-day expiry)

### Signed URL Security
- Generated URLs expire after 7 days
- Each file access generates a new URL if expired
- URLs are cached to reduce API calls
- Only students and the organization reviewing the application can access files

## Setup Instructions

### 1. Update Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Ensure your `.env` file has:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 3. Create Supabase Bucket
In your Supabase dashboard:
1. Go to **Storage** section
2. Create a new bucket named **"applications"**
3. Set bucket to **Private** (only authenticated users)
4. Update your Supabase RLS policies to allow:
   - Upload: User can upload to their own student folder
   - Download: User can download their own files or organization can download applicant files

### 4. Run Migration
```bash
python manage.py migrate
```

### 5. (Optional) Migrate Existing Files
For existing applications with local files, you can manually trigger upload:

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
            signed_url = SupabaseStorageManager.get_signed_url(result['path'])
            if signed_url:
                from datetime import timedelta
                from django.utils import timezone
                app.resume_signed_url = signed_url
                app.signed_url_expires_at = timezone.now() + timedelta(days=7)
            app.save()
```

## File Structure
```
CampusLink/
├── Myapp/
│   ├── models.py (Updated - Application model)
│   └── migrations/
│       └── 0011_add_supabase_storage_fields.py (New)
├── MyLogin/
│   ├── supabase_storage.py (New - Storage utility)
│   ├── views.py (Updated)
│   └── urls.py (Updated)
├── requirements.txt (Updated)
└── CampusLink/
    └── settings.py (No changes needed)
```

## API Reference

### SupabaseStorageManager Class

#### `upload_resume(file_obj, student_id, application_id)`
Uploads a resume file to Supabase storage.

**Parameters:**
- `file_obj` - File object from Django form
- `student_id` - ID of the student uploading
- `application_id` - ID of the application

**Returns:**
```python
{
    'success': bool,
    'path': str or None,  # Path in bucket if successful
    'error': str or None  # Error message if failed
}
```

#### `get_signed_url(file_path, expires_in=None)`
Generates a signed URL for accessing a file.

**Parameters:**
- `file_path` - Path to file in bucket
- `expires_in` - Expiry time in seconds (default: 604800 = 7 days)

**Returns:**
- `str` - Signed URL for accessing the file, or None if error

#### `delete_file(file_path)`
Deletes a file from Supabase storage.

**Parameters:**
- `file_path` - Path to file in bucket

**Returns:**
```python
{
    'success': bool,
    'error': str or None
}
```

#### `file_exists(file_path)`
Checks if a file exists in Supabase storage.

**Parameters:**
- `file_path` - Path to file in bucket

**Returns:**
- `bool` - True if file exists

#### `download_file(file_path)`
Downloads a file from Supabase storage.

**Parameters:**
- `file_path` - Path to file in bucket

**Returns:**
- `bytes` - File content, or None if error

## Benefits

1. **Cross-User Access** - Organizations can now view files uploaded by students
2. **Secure URLs** - Signed URLs with expiration ensure only authorized access
3. **Scalability** - Files are stored in cloud, not local server
4. **Backward Compatibility** - Falls back to local files if Supabase upload fails
5. **URL Caching** - Reduces API calls by caching signed URLs
6. **Error Handling** - Graceful degradation if Supabase is unavailable

## Security Considerations

1. **Access Control** - Only students and their applying organization can access files
2. **Signed URLs** - Expire after 7 days, preventing long-term access
3. **Private Bucket** - Requires authentication to access
4. **RLS Policies** - Supabase Row Level Security ensures data isolation

## Testing

### Test File Upload
1. Go to student dashboard
2. Apply for an opportunity
3. Upload resume
4. Check application details as organization
5. Verify resume can be downloaded

### Test File Access
1. As student - create application
2. As organization - view applicant details
3. Verify resume download works
4. Check signed URL in browser (should work)
5. Wait 7 days (or modify expiry) and verify new URL is generated

## Troubleshooting

### "Supabase upload error" appears
- Check SUPABASE_URL and SUPABASE_KEY in .env
- Verify bucket "applications" exists and is private
- Check Supabase RLS policies allow uploads

### Resume downloads 404
- Verify file exists in Supabase bucket
- Check signed URL has not expired
- Verify access control (student/organization check)

### "Access denied" when downloading
- Ensure user is either the student who uploaded or the organization reviewing
- Check that posting belongs to the organization

## Future Enhancements

1. **Multiple File Support** - Store multiple documents (transcripts, portfolio, etc.)
2. **File Version Control** - Keep multiple versions of uploaded files
3. **Resume Preview** - Show file preview instead of download
4. **Bulk Upload** - Support uploading multiple files at once
5. **File Expiration** - Auto-delete files after application closes
6. **Virus Scanning** - Add malware scanning on upload
7. **Compression** - Compress large files for faster transfer

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Supabase documentation: https://supabase.com/docs
3. Check application logs for error messages
4. Ensure migration was run: `python manage.py migrate`
