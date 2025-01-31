"""Base CSV processor module."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Generator
import pandas as pd
from werkzeug.datastructures import FileStorage
from flask import current_app
from flask_login import current_user
import os
import logging
from datetime import datetime, UTC
import csv
import shutil

from app import db
from app.modules.stores.models import Store
from ..validators.base import BaseCSVValidator
from ..constants import CSV_COLUMNS, ERROR_MESSAGES
from ..models.csv_file import CSVFile
from ..models.upload_history import UploadHistory
from ..utils import (
    validate_file_size,
    validate_file_type,
    generate_safe_filename,
    get_file_hash,
    cleanup_temp_files,
    create_upload_folders,
    FileValidationError
)

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000  # Number of rows to process at once

class ProcessingStatus:
    """Class to track processing status."""
    def __init__(self):
        self.total_rows = 0
        self.processed_rows = 0
        self.current_chunk = 0
        self.errors = []
        self.warnings = []
        self.status = "initializing"  # initializing, processing, completed, failed
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary."""
        return {
            "total_rows": self.total_rows,
            "processed_rows": self.processed_rows,
            "progress": round((self.processed_rows / self.total_rows * 100) if self.total_rows > 0 else 0, 2),
            "current_chunk": self.current_chunk,
            "errors": self.errors,
            "warnings": self.warnings,
            "status": self.status
        }

class BaseCSVProcessor(ABC):
    """Abstract base class for CSV processing."""
    
    def __init__(self, report_type: str):
        """Initialize the CSV processor."""
        self.report_type = report_type
        self.validator = BaseCSVValidator()
        self.processing_status = ProcessingStatus()
        self.csv_file = None
        self.upload_history = None
        
    def process_file(self, file: FileStorage, user_id: int) -> Tuple[bool, str]:
        """Process the uploaded CSV file.
        
        Args:
            file: The uploaded file
            user_id: ID of the user uploading the file
            
        Returns:
            Tuple[bool, str]: (success status, error message)
        """
        try:
            # Create upload directories
            processed_path, temp_path = create_upload_folders()
            
            # Generate safe filename
            safe_filename = generate_safe_filename(file.filename, user_id)
            temp_file_path = os.path.join(temp_path, safe_filename)
            
            # Save file temporarily
            file.save(temp_file_path)
            
            # Get file size and debug info
            file_size = os.path.getsize(temp_file_path)
            logger.info(f"File size: {file_size} bytes")
            
            with open(temp_file_path, 'rb') as f:
                content_preview = f.read(200)
            logger.info(f"Raw file content (first 200 bytes): {content_preview}")
            
            # Get processed path
            processed_file_path = os.path.join(processed_path, safe_filename)
            
            # Detect encoding
            encoding = self._detect_file_encoding(temp_file_path)
            
            # First validate if store_id column exists
            df_check = pd.read_csv(temp_file_path, encoding=encoding, nrows=1)
            if 'store_id' not in df_check.columns:
                cleanup_temp_files(temp_file_path)
                return False, "CSV file must contain 'store_id' column"
            
            # Get first store_id from CSV for the file record
            first_store_id = int(df_check['store_id'].iloc[0])
            
            # Validate access to first store
            access_valid, error_msg = self.validate_store_access(first_store_id, user_id)
            if not access_valid:
                cleanup_temp_files(temp_file_path)
                return False, error_msg
            
            # Create CSV file record
            csv_file = CSVFile(
                filename=safe_filename,
                file_type=self.report_type,
                file_size=file_size,
                file_path=processed_file_path,
                user_id=user_id,
                store_id=first_store_id
            )
            db.session.add(csv_file)
            db.session.flush()
            
            # Create upload history record
            upload_history = UploadHistory(
                csv_file_id=csv_file.id,
                status='processing',
                started_at=datetime.now(UTC)
            )
            db.session.add(upload_history)
            db.session.commit()
            
            self.csv_file = csv_file
            self.upload_history = upload_history
            
            # Process file in chunks
            chunk_iterator = pd.read_csv(
                temp_file_path,
                encoding=encoding,
                chunksize=CHUNK_SIZE,
                on_bad_lines='warn'
            )
            
            total_rows = 0
            for chunk_idx, chunk in enumerate(chunk_iterator, 1):
                # Validate store access for each unique store in chunk
                chunk_store_ids = chunk['store_id'].unique()
                for store_id in chunk_store_ids:
                    access_valid, error_msg = self.validate_store_access(int(store_id), user_id)
                    if not access_valid:
                        # Update history with error
                        upload_history.status = 'failed'
                        upload_history.error_message = error_msg
                        upload_history.completed_at = datetime.now(UTC)
                        db.session.commit()
                        
                        cleanup_temp_files(temp_file_path)
                        return False, error_msg
                
                # Update processing status
                self.processing_status.current_chunk = chunk_idx
                if chunk_idx == 1:
                    total_rows = len(chunk)
                
                # Save chunk data
                try:
                    self.save_data(chunk, user_id)
                    total_rows += len(chunk)
                    
                    # Update upload history progress
                    if self.upload_history:
                        self.upload_history.rows_processed = total_rows
                        db.session.commit()
                        
                except Exception as e:
                    error_msg = f"Error saving chunk {chunk_idx}: {str(e)}"
                    logger.exception(error_msg)
                    
                    # Update history with error
                    upload_history.status = 'failed'
                    upload_history.error_message = error_msg
                    upload_history.completed_at = datetime.now(UTC)
                    db.session.commit()
                    
                    cleanup_temp_files(temp_file_path)
                    return False, error_msg
            
            # Move file to processed directory
            shutil.move(temp_file_path, processed_file_path)
            
            # Update history
            upload_history.status = 'completed'
            upload_history.completed_at = datetime.now(UTC)
            upload_history.rows_processed = total_rows
            db.session.commit()
            
            return True, "File processed successfully"
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            logger.exception(error_msg)
            
            if self.upload_history:
                self.upload_history.status = 'failed'
                self.upload_history.error_message = error_msg
                self.upload_history.completed_at = datetime.now(UTC)
                db.session.commit()
            
            # Clean up temp file if it exists
            if 'temp_file_path' in locals():
                cleanup_temp_files(temp_file_path)
            
            return False, error_msg

    def _detect_file_encoding(self, file_path: str) -> str:
        """
        Dosyanın encoding'ini tespit et ve gerekirse dönüştür.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            str: Tespit edilen encoding
        """
        encodings = ['utf-8', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except UnicodeDecodeError:
                continue
                
        return 'utf-8'  # Default to UTF-8 if no encoding works
        
    def _handle_error(self, error_msg: str) -> Tuple[bool, str]:
        """Handle processing error."""
        self.processing_status.status = "failed"
        self.processing_status.errors.append(error_msg)
        logger.error(error_msg)
        return False, error_msg
        
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        return self.processing_status.to_dict()
        
    def validate_store_access(self, store_id: int, user_id: int) -> Tuple[bool, str]:
        """Validate user has access to store.
        
        Args:
            store_id: Store ID to validate access for
            user_id: User ID to validate access for
            
        Returns:
            Tuple[bool, str]: (success status, error message)
        """
        if not store_id:
            return False, "Store ID is required"

        store = Store.query.filter_by(id=store_id, user_id=user_id).first()
        if not store:
            return False, f"You don't have access to store: {store_id}"

        return True, ""

    @abstractmethod
    def save_data(self, df: pd.DataFrame, user_id: int) -> None:
        """Save the processed data to the database."""
        pass