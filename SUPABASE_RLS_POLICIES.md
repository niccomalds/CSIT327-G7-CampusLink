# Supabase RLS (Row Level Security) Policy Configuration

## Overview
These are the recommended Row Level Security policies for the "applications" bucket in Supabase to ensure secure file access.

## Bucket Configuration

1. **Bucket Name**: `applications`
2. **Privacy**: `Private` (requires authentication)
3. **Allowed File Types**: PDF, DOC, DOCX (enforced in application code)

## RLS Policies

### Policy 1: Allow Students to Upload Their Own Files

**Name**: `allow_student_upload`
**Target Role**: `authenticated`
**Operation**: `INSERT`
**Expression**:
```sql
(auth.uid()::text = (storage.foldername(name))[1])
```

**Explanation**: Allows users to upload files to folders matching their user ID.

---

### Policy 2: Allow Students to Read Their Own Files

**Name**: `allow_student_read_own`
**Target Role**: `authenticated`
**Operation**: `SELECT`
**Expression**:
```sql
(auth.uid()::text = (storage.foldername(name))[1])
```

**Explanation**: Allows users to read files they uploaded (in their user ID folder).

---

### Policy 3: Allow Organizations to Read Applicant Files

**Name**: `allow_org_read_applications`
**Target Role**: `authenticated`
**Operation**: `SELECT`
**Expression**:
```sql
EXISTS (
  SELECT 1 FROM public.myapp_posting p
  JOIN public.myapp_application a ON a.posting_id = p.id
  WHERE p.organization_id = auth.uid()
  AND a.id = (storage.foldername(name))[2]::integer
)
```

**Explanation**: Allows organization users to read files from applications to their postings.

---

### Policy 4: Allow Students to Delete Their Own Files

**Name**: `allow_student_delete_own`
**Target Role**: `authenticated`
**Operation**: `DELETE`
**Expression**:
```sql
(auth.uid()::text = (storage.foldername(name))[1])
```

**Explanation**: Allows users to delete files they uploaded.

---

## How to Add These Policies

### Using Supabase Dashboard:

1. Go to **Storage** → **applications** bucket
2. Click the **Policies** tab
3. Click **New Policy**
4. Select **Create a policy from scratch**
5. Enter the policy details from above
6. Click **Review**
7. Click **Save policy**

### Using SQL Editor:

Paste the following SQL in the SQL Editor:

```sql
-- Policy 1: Allow students to upload
CREATE POLICY allow_student_upload
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'applications'
  AND (auth.uid()::text = (storage.foldername(name))[1])
);

-- Policy 2: Allow students to read own files
CREATE POLICY allow_student_read_own
ON storage.objects FOR SELECT
USING (
  bucket_id = 'applications'
  AND (auth.uid()::text = (storage.foldername(name))[1])
);

-- Policy 3: Allow organizations to read applicant files
CREATE POLICY allow_org_read_applications
ON storage.objects FOR SELECT
USING (
  bucket_id = 'applications'
  AND EXISTS (
    SELECT 1 FROM public.myapp_posting p
    JOIN public.myapp_application a ON a.posting_id = p.id
    WHERE p.organization_id = auth.uid()
    AND a.id = (storage.foldername(name))[2]::integer
  )
);

-- Policy 4: Allow students to delete own files
CREATE POLICY allow_student_delete_own
ON storage.objects FOR DELETE
USING (
  bucket_id = 'applications'
  AND (auth.uid()::text = (storage.foldername(name))[1])
);
```

## File Path Structure

Files are stored with the following structure:

```
applications/
└── resumes/
    └── {student_id}/
        └── {application_id}.pdf
```

Example:
```
applications/
└── resumes/
    └── 42/
        └── 123.pdf
```

Where:
- `42` = Student user ID
- `123` = Application ID
- `.pdf` = File extension (based on uploaded file type)

## Testing RLS Policies

1. Upload a file as a student
2. Try to access the file as the same student (should work)
3. Try to access the file as a different student (should fail)
4. Try to access the file as the organization (should work if they have an application)

## Security Notes

- **Signed URLs**: The application generates 7-day signed URLs which bypass RLS checks
- **Expiration**: After 7 days, new signed URLs must be generated
- **Access Logging**: Monitor storage access in Supabase dashboard
- **File Size Limits**: Consider adding file size restrictions in policies if needed

## Troubleshooting

### "Access Denied" on Upload
- Check that user is authenticated
- Verify bucket privacy is set to "Private"
- Ensure INSERT policy is enabled

### "Access Denied" on Download via Signed URL
- Check that SELECT policy is enabled
- Verify file exists in expected path
- Check if organization has access to the application

### Policies Not Working
- Ensure policies are enabled (toggle switch on)
- Check table/bucket names match exactly
- Verify auth.uid() is returning correct user ID
- Check database schema for correct table names

## Additional Resources

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage Policies Guide](https://supabase.com/docs/guides/storage#managing-access)
- [SQL Functions Reference](https://supabase.com/docs/guides/database/functions)
