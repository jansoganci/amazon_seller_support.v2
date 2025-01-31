"""
Utility functions for CSV upload."""

import os
from typing import Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import hashlib
import shutil
from datetime import datetime
import pytz

from flask import current_app

class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass

def validate_file_size(file: FileStorage) -> Tuple[bool, str]:
    """
    Validate file size is within allowed limits.
    
    Args:
        file: The uploaded file
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)  # Default 10MB
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > max_size:
        return False, f"File size ({size/1024/1024:.1f}MB) exceeds the maximum allowed size ({max_size/1024/1024:.1f}MB)"
        
    if size == 0:
        return False, "File is empty. Please upload a valid CSV file."
        
    return True, ""

def validate_file_type(file: FileStorage) -> Tuple[bool, str]:
    """
    Validate file type is CSV.
    
    Args:
        file: The uploaded file
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not file.filename:
        return False, "No filename provided. Please select a valid CSV file."
        
    if not file.filename.lower().endswith('.csv'):
        return False, f"Invalid file type: '{os.path.splitext(file.filename)[1]}'. Only CSV files are allowed."
        
    return True, ""

def generate_safe_filename(filename: str, user_id: int) -> str:
    """
    Generate a safe filename with user_id prefix.
    
    Args:
        filename: Original filename
        user_id: User ID
        
    Returns:
        str: Safe filename
    """
    base = secure_filename(filename)
    name, ext = os.path.splitext(base)
    timestamp = datetime.now(pytz.UTC).strftime('%Y%m%d_%H%M%S')
    return f"{user_id}_{timestamp}_{name}{ext}"

def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of file.
    
    Args:
        file_path: Path to file
        
    Returns:
        str: File hash
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    return sha256_hash.hexdigest()

def create_upload_folders() -> Tuple[str, str]:
    """
    Create necessary upload folders.
    
    Returns:
        Tuple[str, str]: (processed_path, temp_path)
        
    Raises:
        FileValidationError: If folder creation fails
    """
    try:
        # Create base upload directory
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        # Create temp directory
        temp_path = os.path.join(upload_dir, 'temp')
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
            
        # Create processed directory
        processed_path = os.path.join(upload_dir, 'processed')
        if not os.path.exists(processed_path):
            os.makedirs(processed_path)
            
        return processed_path, temp_path
        
    except Exception as e:
        raise FileValidationError(f"Failed to create upload directories: {str(e)}")

def cleanup_temp_files(temp_file_path: str) -> None:
    """
    Clean up temporary files.
    
    Args:
        temp_file_path: Path to temp file
    """
    try:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    except Exception as e:
        current_app.logger.error(f"Failed to cleanup temp file {temp_file_path}: {str(e)}")
