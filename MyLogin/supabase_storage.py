"""
Supabase Storage Utility Module
Handles file uploads, downloads, and signed URL generation for Supabase buckets
"""
import os
from datetime import timedelta
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from MyLogin.supabase_client import supabase


class SupabaseStorageManager:
    """Manages file uploads and downloads from Supabase buckets"""
    
    RESUME_BUCKET = 'applications'
    RESUMABLE_BUCKET = 'applications'
    SIGNED_URL_EXPIRY = 604800  # 7 days in seconds
    
    @staticmethod
    def upload_resume(file_obj, student_id, application_id):
        """
        Upload a resume file to Supabase storage
        
        Args:
            file_obj: File object from Django form
            student_id: ID of the student uploading the file
            application_id: ID of the application
            
        Returns:
            dict: {'success': bool, 'path': str, 'error': str or None}
        """
        try:
            # Generate unique file path: resumes/{student_id}/{application_id}_{filename}
            original_filename = file_obj.name
            file_extension = os.path.splitext(original_filename)[1]
            
            # Create unique path to avoid conflicts
            file_path = f"resumes/{student_id}/{application_id}{file_extension}"
            
            # Read file content
            file_content = file_obj.read()
            
            # Upload to Supabase
            response = supabase.storage.from_bucket(
                SupabaseStorageManager.RESUME_BUCKET
            ).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "cacheControl": "max-age=3600",
                    "contentType": file_obj.content_type or "application/octet-stream"
                }
            )
            
            return {
                'success': True,
                'path': file_path,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'path': None,
                'error': str(e)
            }
    
    @staticmethod
    def get_signed_url(file_path, expires_in=None):
        """
        Generate a signed URL for accessing a file
        
        Args:
            file_path: Path to the file in the bucket
            expires_in: Expiry time in seconds (default: 7 days)
            
        Returns:
            str: Signed URL for accessing the file
        """
        try:
            if expires_in is None:
                expires_in = SupabaseStorageManager.SIGNED_URL_EXPIRY
            
            response = supabase.storage.from_bucket(
                SupabaseStorageManager.RESUME_BUCKET
            ).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            return response['signedURL']
            
        except Exception as e:
            print(f"Error generating signed URL: {str(e)}")
            return None
    
    @staticmethod
    def delete_file(file_path):
        """
        Delete a file from Supabase storage
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            dict: {'success': bool, 'error': str or None}
        """
        try:
            supabase.storage.from_bucket(
                SupabaseStorageManager.RESUME_BUCKET
            ).remove([file_path])
            
            return {
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def file_exists(file_path):
        """
        Check if a file exists in Supabase storage
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            response = supabase.storage.from_bucket(
                SupabaseStorageManager.RESUME_BUCKET
            ).list(path=os.path.dirname(file_path))
            
            file_name = os.path.basename(file_path)
            return any(item['name'] == file_name for item in response)
            
        except Exception as e:
            print(f"Error checking file existence: {str(e)}")
            return False
    
    @staticmethod
    def download_file(file_path):
        """
        Download a file from Supabase storage
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            bytes: File content or None if error
        """
        try:
            response = supabase.storage.from_bucket(
                SupabaseStorageManager.RESUME_BUCKET
            ).download(path=file_path)
            
            return response
            
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None
