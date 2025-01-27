"""
Utility functions for CSV file handling and validation.
"""

import os
import logging
from typing import Tuple, Optional
from datetime import datetime
from werkzeug.datastructures import FileStorage
import magic  # python-magic kütüphanesi için
import hashlib
import pandas as pd  # Import pandas
from flask import current_app

logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = ['text/csv', 'application/csv', 'application/vnd.ms-excel']
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for reading

class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass

def get_file_mime_type(file_path: str) -> str:
    """
    Get MIME type of a file using python-magic.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: MIME type of the file
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception as e:
        logger.error(f"Error getting MIME type: {str(e)}")
        return ""

def validate_file_size(file: FileStorage) -> Tuple[bool, str]:
    """
    Validate file size against MAX_FILE_SIZE limit.
    
    Args:
        file: The uploaded file object
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if size > MAX_FILE_SIZE:
            return False, f"File size cannot exceed {MAX_FILE_SIZE/1024/1024}MB"
        return True, ""
    except Exception as e:
        logger.error(f"Error validating file size: {str(e)}")
        return False, "Could not validate file size"

def validate_file_type(file: FileStorage) -> Tuple[bool, str]:
    """
    Validate file type using extension and content check.
    
    Args:
        file: The uploaded file object
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Dosya uzantısını kontrol et
        if not file.filename.lower().endswith('.csv'):
            return False, f"Invalid file type. Allowed types: CSV"

        # Dosyayı geçici olarak kaydet
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', file.filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        file.save(temp_path)

        # Dosya içeriğini kontrol et
        try:
            # Önce encoding'i tespit et
            import chardet
            with open(temp_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                detected_encoding = result['encoding'] or 'utf-8'
            
            # Pandas ile okumayı dene
            try:
                pd.read_csv(temp_path, encoding=detected_encoding, nrows=1)
                return True, ""
            except pd.errors.EmptyDataError:
                return False, "CSV file is empty"
            except Exception as e:
                logger.error(f"Error reading CSV with pandas: {str(e)}")
                # Pandas ile okunamazsa manuel kontrol et
                with open(temp_path, 'r', encoding=detected_encoding) as f:
                    first_line = f.readline().strip()
                    if ',' in first_line and any(c.isalnum() for c in first_line):
                        return True, ""
                    return False, "File does not appear to be a valid CSV file. Please ensure it is comma-separated."
                        
        except Exception as e:
            logger.error(f"Error validating file content: {str(e)}")
            return False, "Could not validate file content. Please ensure it is a valid CSV file."
        finally:
            try:
                os.remove(temp_path)  # Temizlik
                logger.info(f"Temporary file deleted: {temp_path}")
            except Exception as e:
                logger.error(f"Error deleting temporary file: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error validating file type: {str(e)}")
        return False, "Could not validate file type"

def generate_safe_filename(original_filename: str, user_id: int) -> str:
    """
    Generate a safe filename with timestamp and user ID.
    
    Args:
        original_filename: Original name of the file
        user_id: ID of the user uploading the file
        
    Returns:
        str: Safe filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename, ext = os.path.splitext(original_filename)
    safe_filename = f"{filename}_{timestamp}_{user_id}{ext}"
    return safe_filename

def get_file_hash(file_path: str) -> Optional[str]:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Optional[str]: File hash or None if error occurs
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {str(e)}")
        return None

def cleanup_temp_files(file_path: str) -> bool:
    """
    Clean up temporary files.
    
    Args:
        file_path: Path to the temporary file
        
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Temporary file deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting temporary file: {str(e)}")
        return False

def create_upload_folders(user_id: int, report_type: str) -> Tuple[str, str]:
    """
    Create necessary folders for file upload.
    
    Args:
        user_id: ID of the user
        report_type: Type of the report being uploaded
        
    Returns:
        Tuple[str, str]: (upload_path, temp_path)
    """
    try:
        # Create main upload directory
        upload_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            str(user_id),
            report_type
        )
        os.makedirs(upload_path, exist_ok=True)
        
        # Create temp directory
        temp_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'temp',
            str(user_id)
        )
        os.makedirs(temp_path, exist_ok=True)
        
        return upload_path, temp_path
    except Exception as e:
        logger.error(f"Error creating upload folders: {str(e)}")
        raise FileValidationError("Error creating folders")
