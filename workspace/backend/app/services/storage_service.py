"""
Professional Storage Service for Routix Platform
Supports local storage, AWS S3, and Cloudflare R2
"""
import os
import uuid
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO, Union
from datetime import datetime, timezone
import httpx
from io import BytesIO

import logging
logger = logging.getLogger(__name__)


class StorageServiceError(Exception):
    """Custom exception for storage service errors"""
    pass


class StorageService:
    """
    Unified storage service supporting multiple backends:
    - Local filesystem (development)
    - AWS S3 (production)
    - Cloudflare R2 (recommended for production)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize storage service with configuration
        
        Args:
            config: Configuration dict with storage settings
        """
        self.config = config or {}
        self.storage_type = self.config.get('STORAGE_TYPE', 'local').lower()
        
        if self.storage_type == 'local':
            self._init_local_storage()
        elif self.storage_type == 's3':
            self._init_s3_storage()
        elif self.storage_type == 'cloudflare_r2':
            self._init_r2_storage()
        else:
            raise StorageServiceError(f"Unsupported storage type: {self.storage_type}")
        
        logger.info(f"Storage service initialized with backend: {self.storage_type}")
    
    def _init_local_storage(self):
        """Initialize local filesystem storage"""
        self.upload_dir = Path(self.config.get('UPLOAD_DIR', './uploads'))
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        (self.upload_dir / 'templates').mkdir(exist_ok=True)
        (self.upload_dir / 'generations').mkdir(exist_ok=True)
        (self.upload_dir / 'user_assets').mkdir(exist_ok=True)
        (self.upload_dir / 'temp').mkdir(exist_ok=True)
        
        logger.info(f"Local storage initialized at: {self.upload_dir}")
    
    def _init_s3_storage(self):
        """Initialize AWS S3 storage"""
        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise StorageServiceError(
                "boto3 is required for S3 storage. Install with: pip install boto3"
            )
        
        aws_access_key = self.config.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = self.config.get('AWS_SECRET_ACCESS_KEY')
        aws_region = self.config.get('AWS_REGION', 'us-east-1')
        self.s3_bucket = self.config.get('S3_BUCKET_NAME')
        
        if not all([aws_access_key, aws_secret_key, self.s3_bucket]):
            raise StorageServiceError(
                "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME "
                "are required for S3 storage"
            )
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
            config=Config(
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'adaptive'}
            )
        )
        
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"S3 storage initialized with bucket: {self.s3_bucket}")
        except Exception as e:
            raise StorageServiceError(f"Failed to connect to S3 bucket: {e}")
    
    def _init_r2_storage(self):
        """Initialize Cloudflare R2 storage"""
        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise StorageServiceError(
                "boto3 is required for R2 storage. Install with: pip install boto3"
            )
        
        r2_account_id = self.config.get('R2_ACCOUNT_ID')
        r2_access_key = self.config.get('R2_ACCESS_KEY_ID')
        r2_secret_key = self.config.get('R2_SECRET_ACCESS_KEY')
        self.r2_bucket = self.config.get('R2_BUCKET_NAME')
        self.r2_public_url = self.config.get('R2_PUBLIC_URL')
        
        if not all([r2_account_id, r2_access_key, r2_secret_key, self.r2_bucket]):
            raise StorageServiceError(
                "R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, and "
                "R2_BUCKET_NAME are required for R2 storage"
            )
        
        r2_endpoint = f"https://{r2_account_id}.r2.cloudflarestorage.com"
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=r2_endpoint,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name='auto',
            config=Config(
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'adaptive'}
            )
        )
        
        try:
            self.s3_client.head_bucket(Bucket=self.r2_bucket)
            logger.info(f"R2 storage initialized with bucket: {self.r2_bucket}")
        except Exception as e:
            raise StorageServiceError(f"Failed to connect to R2 bucket: {e}")
    
    async def upload_file(
        self,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        folder: str = 'uploads',
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to storage
        
        Args:
            file_data: File data as bytes or file-like object
            filename: Original filename
            folder: Folder/prefix for the file
            content_type: MIME type of the file
            metadata: Additional metadata to store
            
        Returns:
            Dict containing file info (url, key, size, etc.)
        """
        try:
            file_ext = Path(filename).suffix
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            file_key = f"{folder}/{unique_filename}"
            
            if isinstance(file_data, bytes):
                data = file_data
            else:
                data = file_data.read()
            
            if not content_type:
                content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            file_hash = hashlib.sha256(data).hexdigest()
            file_size = len(data)
            
            if self.storage_type == 'local':
                result = await self._upload_local(file_key, data, content_type, metadata)
            elif self.storage_type in ['s3', 'cloudflare_r2']:
                result = await self._upload_s3(file_key, data, content_type, metadata)
            else:
                raise StorageServiceError(f"Unsupported storage type: {self.storage_type}")
            
            return {
                'success': True,
                'key': file_key,
                'url': result['url'],
                'filename': unique_filename,
                'original_filename': filename,
                'size': file_size,
                'content_type': content_type,
                'hash': file_hash,
                'storage_type': self.storage_type,
                'uploaded_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise StorageServiceError(f"Failed to upload file: {str(e)}")
    
    async def _upload_local(
        self,
        file_key: str,
        data: bytes,
        content_type: str,
        metadata: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Upload file to local storage"""
        file_path = self.upload_dir / file_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_bytes(data)
        
        url = f"/uploads/{file_key}"
        
        return {'url': url}
    
    async def _upload_s3(
        self,
        file_key: str,
        data: bytes,
        content_type: str,
        metadata: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Upload file to S3 or R2"""
        import asyncio
        
        bucket = self.r2_bucket if self.storage_type == 'cloudflare_r2' else self.s3_bucket
        
        extra_args = {
            'ContentType': content_type,
            'ACL': 'public-read'
        }
        
        if metadata:
            extra_args['Metadata'] = metadata
        
        await asyncio.to_thread(
            self.s3_client.put_object,
            Bucket=bucket,
            Key=file_key,
            Body=data,
            **extra_args
        )
        
        if self.storage_type == 'cloudflare_r2' and self.r2_public_url:
            url = f"{self.r2_public_url}/{file_key}"
        else:
            url = f"https://{bucket}.s3.amazonaws.com/{file_key}"
        
        return {'url': url}
    
    async def download_file(self, file_key: str) -> bytes:
        """
        Download a file from storage
        
        Args:
            file_key: File key/path in storage
            
        Returns:
            File data as bytes
        """
        try:
            if self.storage_type == 'local':
                return await self._download_local(file_key)
            elif self.storage_type in ['s3', 'cloudflare_r2']:
                return await self._download_s3(file_key)
            else:
                raise StorageServiceError(f"Unsupported storage type: {self.storage_type}")
        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise StorageServiceError(f"Failed to download file: {str(e)}")
    
    async def _download_local(self, file_key: str) -> bytes:
        """Download file from local storage"""
        file_path = self.upload_dir / file_key
        
        if not file_path.exists():
            raise StorageServiceError(f"File not found: {file_key}")
        
        return file_path.read_bytes()
    
    async def _download_s3(self, file_key: str) -> bytes:
        """Download file from S3 or R2"""
        import asyncio
        
        bucket = self.r2_bucket if self.storage_type == 'cloudflare_r2' else self.s3_bucket
        
        response = await asyncio.to_thread(
            self.s3_client.get_object,
            Bucket=bucket,
            Key=file_key
        )
        
        return response['Body'].read()
    
    async def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            file_key: File key/path in storage
            
        Returns:
            True if successful
        """
        try:
            if self.storage_type == 'local':
                return await self._delete_local(file_key)
            elif self.storage_type in ['s3', 'cloudflare_r2']:
                return await self._delete_s3(file_key)
            else:
                raise StorageServiceError(f"Unsupported storage type: {self.storage_type}")
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            raise StorageServiceError(f"Failed to delete file: {str(e)}")
    
    async def _delete_local(self, file_key: str) -> bool:
        """Delete file from local storage"""
        file_path = self.upload_dir / file_key
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    async def _delete_s3(self, file_key: str) -> bool:
        """Delete file from S3 or R2"""
        import asyncio
        
        bucket = self.r2_bucket if self.storage_type == 'cloudflare_r2' else self.s3_bucket
        
        await asyncio.to_thread(
            self.s3_client.delete_object,
            Bucket=bucket,
            Key=file_key
        )
        
        return True
    
    async def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in storage
        
        Args:
            file_key: File key/path in storage
            
        Returns:
            True if file exists
        """
        try:
            if self.storage_type == 'local':
                return (self.upload_dir / file_key).exists()
            elif self.storage_type in ['s3', 'cloudflare_r2']:
                import asyncio
                bucket = self.r2_bucket if self.storage_type == 'cloudflare_r2' else self.s3_bucket
                
                try:
                    await asyncio.to_thread(
                        self.s3_client.head_object,
                        Bucket=bucket,
                        Key=file_key
                    )
                    return True
                except:
                    return False
            return False
        except Exception as e:
            logger.error(f"File existence check failed: {e}")
            return False
    
    async def get_file_info(self, file_key: str) -> Dict[str, Any]:
        """
        Get file metadata
        
        Args:
            file_key: File key/path in storage
            
        Returns:
            Dict containing file metadata
        """
        try:
            if self.storage_type == 'local':
                return await self._get_local_file_info(file_key)
            elif self.storage_type in ['s3', 'cloudflare_r2']:
                return await self._get_s3_file_info(file_key)
            else:
                raise StorageServiceError(f"Unsupported storage type: {self.storage_type}")
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            raise StorageServiceError(f"Failed to get file info: {str(e)}")
    
    async def _get_local_file_info(self, file_key: str) -> Dict[str, Any]:
        """Get file info from local storage"""
        file_path = self.upload_dir / file_key
        
        if not file_path.exists():
            raise StorageServiceError(f"File not found: {file_key}")
        
        stat = file_path.stat()
        
        return {
            'key': file_key,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            'content_type': mimetypes.guess_type(file_path)[0],
            'storage_type': 'local'
        }
    
    async def _get_s3_file_info(self, file_key: str) -> Dict[str, Any]:
        """Get file info from S3 or R2"""
        import asyncio
        
        bucket = self.r2_bucket if self.storage_type == 'cloudflare_r2' else self.s3_bucket
        
        response = await asyncio.to_thread(
            self.s3_client.head_object,
            Bucket=bucket,
            Key=file_key
        )
        
        return {
            'key': file_key,
            'size': response.get('ContentLength'),
            'modified': response.get('LastModified').isoformat() if response.get('LastModified') else None,
            'content_type': response.get('ContentType'),
            'metadata': response.get('Metadata', {}),
            'storage_type': self.storage_type
        }
    
    async def get_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600,
        operation: str = 'get_object'
    ) -> str:
        """
        Generate a presigned URL for temporary access
        
        Args:
            file_key: File key/path in storage
            expiration: URL expiration time in seconds
            operation: S3 operation (get_object, put_object)
            
        Returns:
            Presigned URL string
        """
        if self.storage_type == 'local':
            return f"/uploads/{file_key}"
        
        elif self.storage_type in ['s3', 'cloudflare_r2']:
            import asyncio
            
            bucket = self.r2_bucket if self.storage_type == 'cloudflare_r2' else self.s3_bucket
            
            url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                operation,
                Params={'Bucket': bucket, 'Key': file_key},
                ExpiresIn=expiration
            )
            
            return url
        
        else:
            raise StorageServiceError(f"Presigned URLs not supported for: {self.storage_type}")
    
    async def upload_from_url(
        self,
        url: str,
        folder: str = 'uploads',
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download a file from URL and upload to storage
        
        Args:
            url: URL to download from
            folder: Folder/prefix for the file
            filename: Optional filename override
            
        Returns:
            Dict containing file info
        """
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                file_data = response.content
                content_type = response.headers.get('content-type')
                
                if not filename:
                    filename = url.split('/')[-1].split('?')[0] or f"{uuid.uuid4().hex}.jpg"
            
            return await self.upload_file(
                file_data=file_data,
                filename=filename,
                folder=folder,
                content_type=content_type
            )
            
        except Exception as e:
            logger.error(f"Failed to upload from URL: {e}")
            raise StorageServiceError(f"Failed to upload from URL: {str(e)}")


def get_storage_service(config: Optional[Dict[str, Any]] = None) -> StorageService:
    """Get or create storage service instance"""
    if config is None:
        from app.core.config import settings
        config = {
            'STORAGE_TYPE': getattr(settings, 'STORAGE_TYPE', 'local'),
            'UPLOAD_DIR': getattr(settings, 'UPLOAD_DIR', './uploads'),
            'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
            'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
            'S3_BUCKET_NAME': os.getenv('S3_BUCKET_NAME'),
            'R2_ACCOUNT_ID': os.getenv('R2_ACCOUNT_ID'),
            'R2_ACCESS_KEY_ID': os.getenv('R2_ACCESS_KEY_ID'),
            'R2_SECRET_ACCESS_KEY': os.getenv('R2_SECRET_ACCESS_KEY'),
            'R2_BUCKET_NAME': os.getenv('R2_BUCKET_NAME'),
            'R2_PUBLIC_URL': os.getenv('R2_PUBLIC_URL'),
        }
    
    return StorageService(config)


storage_service = get_storage_service()
