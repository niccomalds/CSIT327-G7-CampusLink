# System Architecture Diagrams

## 1. File Upload Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      STUDENT UPLOAD FLOW                        │
└─────────────────────────────────────────────────────────────────┘

  STUDENT                    DJANGO                   SUPABASE
    │                          │                         │
    │  1. Submit Application   │                         │
    ├─────────────────────────>│                         │
    │                          │                         │
    │                 2. Create Application              │
    │                 with local FileField              │
    │                          │                         │
    │                 3. Upload Resume (async)          │
    │                          ├────────────────────────>│
    │                          │                         │
    │                          │   4. Store in Bucket    │
    │                          │     resumes/{id}/{id}   │
    │                          │                         │
    │                          │<────────────────────────┤
    │                          │     Path Returned       │
    │                          │                         │
    │                 5. Update Application              │
    │                 - resume_supabase_path             │
    │                 - resume_signed_url                │
    │                 - uses_supabase_storage=True       │
    │                          │                         │
    │   Success Response       │                         │
    │<─────────────────────────┤                         │
    │                          │                         │
```

## 2. File Access & Download Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   ORGANIZATION DOWNLOAD FLOW                    │
└─────────────────────────────────────────────────────────────────┘

  ORG USER                   DJANGO                   SUPABASE
    │                          │                         │
    │  1. View Applicant       │                         │
    ├─────────────────────────>│                         │
    │                          │                         │
    │           2. get_application_details()            │
    │                          │                         │
    │       3. application.get_resume_url()             │
    │                          │                         │
    │           ┌──────────────┴──────────────┐         │
    │           │                             │         │
    │    4a. Check if Supabase    4b. Check if Supabase
    │        storage + valid URL       URL expired
    │           │                     │
    │        YES → Return URL      YES → Generate New URL
    │           │                     │
    │        NO → Use local file      Generate
    │           │                     ├────────────────>│
    │           │                     │                 │
    │           │          5. Create Signed URL        │
    │           │                     │<────────────────┤
    │           │                     │  URL (7-day exp)
    │           │          6. Cache URL + Expiry       │
    │           │                     │                 │
    │    Return URL to Frontend       │                 │
    │<───────────────────────────────┤                 │
    │                                 │                 │
    │  7. Download Resume             │                 │
    ├────────────────────────────────>│                 │
    │                                 │                 │
    │              8. Validate Access  │                 │
    │         (is student or org?)      │                 │
    │                                 │                 │
    │           Access OK              │                 │
    │                                 │                 │
    │         9. Return File Content   │                 │
    │<────────────────────────────────┤                 │
    │                                 │                 │
```

## 3. Data Model Relationship

```
┌──────────────────────────────────────────────────────────────┐
│                     DATABASE SCHEMA                          │
└──────────────────────────────────────────────────────────────┘

    User                      Organization
    ├── id                     ├── id
    ├── email                  ├── name
    └── ...                    └── ...
        │                          │
        │ student                 │ organization
        │                         │
        ├─────────────────────────┤
                    │
                    ▼
            Application
            ├── id (PK)
            ├── student_id (FK) ─────────> User
            ├── posting_id (FK) ─────────> Posting
            ├── resume (FileField)
            ├── note
            ├── status
            ├── created_at
            ├── updated_at
            │
            │ ┌─── NEW Supabase Fields ───┐
            ├── resume_supabase_path ──> Supabase Bucket
            ├── resume_signed_url ──────> Cache
            ├── signed_url_expires_at ──> Expiry
            └── uses_supabase_storage ──> Flag
                    │
                    ▼
            Posting
            ├── id (PK)
            ├── organization_id (FK) ──> User(org)
            ├── title
            └── ...
```

## 4. Security & Access Control

```
┌──────────────────────────────────────────────────────────────┐
│              ACCESS CONTROL MATRIX                           │
└──────────────────────────────────────────────────────────────┘

                    Can Upload    Can Download    Can Delete
Student             Own files     Own files       Own files
  │
  └─ resume.pdf

Organization        NO            Applicant       NO
  │                               files from
  └─ Views applicant              their postings

Other Student       NO            NO              NO

Admin               YES (via      YES (via        YES (via
                    API)          API)            API)


┌──────────────────────────────────────────────────────────────┐
│            SUPABASE RLS POLICIES FLOW                        │
└──────────────────────────────────────────────────────────────┘

User Request
    │
    ├─── Authenticated? ──NO──> DENY
    │
    YES
    │
    ├─── Operation Type?
    │
    ├─ INSERT (Upload)
    │  └─ Check: auth.uid() == path_folder
    │     └─ YES: ALLOW  |  NO: DENY
    │
    ├─ SELECT (Download/View)
    │  └─ Check: User's own file OR Organization's applicant
    │     └─ YES: ALLOW  |  NO: DENY
    │
    ├─ DELETE
    │  └─ Check: auth.uid() == path_folder
    │     └─ YES: ALLOW  |  NO: DENY
    │
    └─ UPDATE (Not allowed by default)
       └─ DENY
```

## 5. File Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│              FILE LIFECYCLE & TIMESTAMPS                     │
└──────────────────────────────────────────────────────────────┘

Application Created
      │
      ├─ resume (local FileField)
      ├─ created_at = NOW
      │
      ▼
Application Submitted
      │
      ├─ Upload to Supabase
      │  └─ Creates: resumes/{id}/{id}.pdf
      │
      ├─ URL Generated
      │  └─ Signed URL (7 day expiry)
      │     └─ Example: https://...?Expires=...&Signature=...
      │
      ├─ Fields Updated
      │  ├─ resume_supabase_path = "resumes/42/123.pdf"
      │  ├─ resume_signed_url = "https://...signed..."
      │  ├─ signed_url_expires_at = NOW + 7 days
      │  └─ uses_supabase_storage = True
      │
      ▼
Day 1-7: Organization Downloads Resume
      │
      ├─ get_resume_url() called
      │  └─ URL still valid
      │  └─ Return cached URL
      │
      ▼
Day 7: URL Expires
      │
      ├─ get_resume_url() called
      │  └─ Check: expired? YES
      │  └─ Generate new signed URL
      │  └─ Update cache
      │  └─ Return new URL
      │
      ▼
Day 365+: Application Archived/Closed
      │
      ├─ (Optional) Delete from Supabase
      │  └─ SupabaseStorageManager.delete_file()
      │
      ├─ Keep local FileField reference
      │  └─ For archive/history
      │
      ▼
```

## 6. Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│               COMPONENT INTERACTION DIAGRAM                  │
└──────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Django Apps   │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    │           │          │
    ▼           ▼          ▼
┌────────┐  ┌──────────┐  ┌────────────┐
│ Views  │  │ Models   │  │ URLs       │
├────────┤  ├──────────┤  ├────────────┤
│student │  │Application│ │/download   │
│_dashbrd│  │- Fields   │ │-resume     │
│create_ │  │- Methods  │ │/get-app-   │
│applictn│  │  get_     │ │details     │
│get_app │  │  resume   │ │            │
│_details│  │  _url()   │ │            │
│download│  │           │ │            │
│_resume │  │Posting    │ │            │
└────┬───┘  │- id       │ └────────────┘
     │      │- org_id   │
     │      └───────────┘
     │
     ▼
┌──────────────────────────────────┐
│  SupabaseStorageManager          │
├──────────────────────────────────┤
│ + upload_resume()                │
│ + get_signed_url()               │
│ + delete_file()                  │
│ + file_exists()                  │
│ + download_file()                │
└────────┬───────────────┬─────────┘
         │               │
         ▼               ▼
┌──────────────────────────────────┐
│    Supabase Client              │
├──────────────────────────────────┤
│ - Handles API calls              │
│ - Manages authentication         │
│ - Provides storage interface     │
└────────┬──────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│    Supabase API / Storage        │
├──────────────────────────────────┤
│ - Authentication                 │
│ - RLS Enforcement                │
│ - Signed URL Generation          │
│ - File Operations                │
│ - Logging & Monitoring           │
└──────────────────────────────────┘
```

## 7. Request Timeline Sequence

```
┌──────────────────────────────────────────────────────────────┐
│        COMPLETE REQUEST-RESPONSE TIMELINE                    │
└──────────────────────────────────────────────────────────────┘

Time  Student                Django              Supabase
T0    │ Submit Form           │                   │
      ├──────────────────────>│                   │
      │  - resume file        │                   │
      │  - note               │                   │
      │  - posting_id         │                   │
      │                       │                   │

T1    │                  Create Application      │
      │                  - Save locally          │
      │                  │                       │

T2    │                  Upload Async            │
      │                  │                       │
      │                  ├──────────────────────>│
      │                  │  Resume file          │

T3    │                  │                  Store file
      │                  │                  resumes/42/123.pdf
      │                  │<──────────────────┤
      │                  │  Path returned

T4    │                  Update Application
      │                  - resume_supabase_path
      │                  - resume_signed_url
      │                  - uses_supabase_storage

T5    │  Success          │                   │
      │<─────────────────┤                   │
      │  Redirect to      │                   │
      │  applications     │                   │


      ─────────────────────────────────────────────────────

      Organization views details

T10   Organization       │
      ├─────────────────>│ GET /get-app-details/123
      │                  │

T11   │             Query Application
      │             - id=123
      │             - Check access (Organization)

T12   │             get_resume_url()
      │             - Check: uses_supabase_storage? YES
      │             - Check: URL valid? YES
      │             - Return cached URL

T13   │  Resume URL       │
      │<─────────────────┤
      │  Signed URL with  │
      │  7-day expiry     │
      │                   │

T14   Organization       │               Supabase
      ├─────────────────────────────────>│
      │  GET /download-resume/123

T15   │             Validate access
      │             - Is organization? YES
      │             - For this posting? YES

T16   │                       GET file
      │                       resumes/42/123.pdf
      │                       ├────────────────>│
      │                       │                 │

T17   │                       │            Return file
      │                       │<────────────────┤
      │                       │  PDF bytes

T18   │  File Download        │
      │<─────────────────────┤
      │  Resume.pdf           │
      │  (saved locally)       │
```

## 8. Error Handling Flow

```
┌──────────────────────────────────────────────────────────────┐
│              ERROR HANDLING FLOWCHART                         │
└──────────────────────────────────────────────────────────────┘

Application Submission
        │
        ▼
Create Local Application
        │
        ├─ OK: Continue
        │
        ▼
Upload to Supabase
        │
        ├─ ERROR: Supabase Error
        │  │
        │  ├─ Log error
        │  ├─ Continue anyway (non-blocking)
        │  └─ Application uses local file (fallback)
        │
        ├─ OK: Continue
        │
        ▼
Update Application Fields
        │
        ├─ OK: Success
        │
        └─ ERROR: Database error
           │
           └─ Log error (critical)

─────────────────────────────────────────────────────────

Download Resume
        │
        ▼
Validate Access
        │
        ├─ ERROR: Access Denied
        │  │
        │  └─ Return 403 error
        │     (Access Denied)
        │
        ├─ OK: Continue
        │
        ▼
Check File Location
        │
        ├─ Supabase Storage?
        │  │
        │  ├─ Check URL valid?
        │  │  │
        │  │  ├─ YES: Return cached URL
        │  │  │
        │  │  └─ NO/EXPIRED:
        │  │     │
        │  │     ├─ Generate new URL
        │  │     │
        │  │     ├─ ERROR: Supabase Error
        │  │     │  │
        │  │     │  └─ Fall back to local
        │  │     │
        │  │     └─ OK: Cache & return new URL
        │  │
        │  └─ Download from Supabase
        │     │
        │     ├─ ERROR: File not found
        │     │  │
        │     │  └─ Return 404 error
        │     │
        │     └─ OK: Return file
        │
        ├─ Local Storage?
        │  │
        │  └─ Return local file
        │
        └─ No file
           │
           └─ Return 404 error
```

---

## Summary

These diagrams show:
1. **Upload Flow** - How files get to Supabase
2. **Access Flow** - How organizations download files
3. **Data Model** - Database relationships
4. **Security** - Access control & RLS policies
5. **File Lifecycle** - Timeline of file management
6. **Architecture** - Component interactions
7. **Request Timeline** - Step-by-step execution
8. **Error Handling** - Error scenarios and fallbacks
