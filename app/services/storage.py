import io
from typing import Optional
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.config import settings


class ObjectStorageService:
    """Service for interacting with RustFS object storage using boto3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.rustfs_endpoint,
            aws_access_key_id=settings.rustfs_access_key,
            aws_secret_access_key=settings.rustfs_secret_key,
            config=Config(signature_version='s3v4'),
            region_name=settings.rustfs_region
        )
        self.bucket_name = settings.rustfs_bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    print(f"Bucket {self.bucket_name} created successfully")
                except ClientError as create_error:
                    print(f"Error creating bucket: {create_error}")
                    raise
            else:
                print(f"Error checking bucket: {e}")
                raise
    
    def upload_file(
        self, 
        file_data: bytes, 
        object_name: str, 
        content_type: str = "application/pdf"
    ) -> bool:
        """Upload file to RustFS object storage"""
        try:
            file_stream = io.BytesIO(file_data)
            self.s3_client.upload_fileobj(
                file_stream,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': content_type}
            )
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False
    
    def download_file(self, object_name: str) -> Optional[bytes]:
        """Download file from RustFS object storage"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return None
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if file exists in RustFS object storage
        
        Args:
            object_name: Object key in the bucket
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True
        except ClientError:
            return False
    
    def get_file_url(self, object_name: str) -> str:
        """Get the URL for a file in object storage"""
        endpoint = settings.rustfs_endpoint.rstrip('/')
        return f"{endpoint}/{self.bucket_name}/{object_name}"
    
    def generate_presigned_url(
        self, 
        object_name: str, 
        expiration: int = 600,
        method: str = 'get_object'
    ) -> Optional[str]:
        """
        Generate a presigned URL for file access
        
        Args:
            object_name: Object key in the bucket
            expiration: URL expiration time in seconds (default: 600 = 10 minutes)
            method: 'get_object' for download, 'put_object' for upload
            
        Returns:
            Presigned URL string or None if error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod=method,
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None


# Singleton instance
storage_service = ObjectStorageService()
