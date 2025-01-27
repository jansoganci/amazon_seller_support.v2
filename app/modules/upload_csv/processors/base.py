"""Base CSV processor module."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Generator
import pandas as pd
from werkzeug.datastructures import FileStorage
from flask import current_app
import os
import logging
from datetime import datetime
import csv

from app import db
from app.models.store import Store
from ..validators.base import BaseCSVValidator
from ..constants import CSV_COLUMNS, ERROR_MESSAGES
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
        
    def process_file(self, file: FileStorage, user_id: int) -> Tuple[bool, str]:
        """Process the uploaded CSV file."""
        try:
            # Reset processing status
            self.processing_status = ProcessingStatus()
            self.processing_status.status = "processing"
            
            # Debug: Dosya içeriğini kontrol et
            content = file.read().decode('utf-8')
            print(f"File content:\n{content[:1000]}")  # İlk 1000 karakteri göster
            file.seek(0)  # Dosya pointer'ı başa al
            
            # Step 1: Validate file size and type
            is_valid, error_msg = validate_file_size(file)
            if not is_valid:
                return self._handle_error(error_msg)
            file.seek(0)  # Pointer'ı tekrar başa al
                
            is_valid, error_msg = validate_file_type(file)
            if not is_valid:
                return self._handle_error(error_msg)
            file.seek(0)  # Pointer'ı tekrar başa al
            
            # Step 2: Create necessary folders
            try:
                upload_path, temp_path = create_upload_folders(user_id, self.report_type)
            except FileValidationError as e:
                return self._handle_error(str(e))
            
            # Step 3: Save file with safe name
            safe_filename = generate_safe_filename(file.filename, user_id)
            temp_file_path = os.path.join(temp_path, safe_filename)
            
            # Dosyayı string olarak kaydet
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Debug: Kaydedilen dosyayı kontrol et
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
                print(f"Saved file content:\n{saved_content[:1000]}")
            
            # Step 4: Process file in chunks
            success = True
            message = ""
            try:
                # Process in chunks
                for success, message in self._process_chunks(temp_file_path, user_id):
                    if not success:
                        break
                
                if success:
                    # Move file to final location if processing successful
                    final_path = os.path.join(upload_path, safe_filename)
                    os.rename(temp_file_path, final_path)
                    return True, "File processed successfully"
                else:
                    return False, message
                    
            finally:
                # Clean up temp file
                cleanup_temp_files(temp_file_path)
                
        except Exception as e:
            return self._handle_error(f"Error processing file: {str(e)}")
            
    def _process_chunks(self, file_path: str, user_id: int) -> Generator[Tuple[bool, str], None, None]:
        """Process CSV file in chunks."""
        try:
            # Debug: Dosya var mı kontrol et
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                yield False, "File does not exist"
                return

            # Debug: Dosya boyutunu kontrol et
            file_size = os.path.getsize(file_path)
            logger.info(f"File size: {file_size} bytes")
            if file_size == 0:
                logger.error("File is empty")
                yield False, "File is empty"
                return

            # Debug: Dosya içeriğini kontrol et
            with open(file_path, 'rb') as f:
                content = f.read()
                logger.info(f"Raw file content (first 200 bytes): {content[:200]}")

            # Önce dosyanın encoding'ini tespit et
            encoding = self._detect_file_encoding(file_path)
            logger.info(f"Detected file encoding: {encoding}")
            
            # Debug: Dosyayı text olarak oku
            with open(file_path, 'r', encoding=encoding) as f:
                first_lines = [next(f) for _ in range(2)]
                logger.info(f"First two lines:\n1: {first_lines[0].strip()}\n2: {first_lines[1].strip() if len(first_lines) > 1 else 'No second line'}")
            
            # CSV dosyasını oku - özel parametrelerle
            try:
                logger.info("Attempting to read CSV with pandas...")
                df = pd.read_csv(file_path, encoding=encoding)
                logger.info(f"Successfully read CSV. Shape: {df.shape}, Columns: {df.columns.tolist()}")
                
                # DataFrame'i chunk'lara böl
                chunk_size = CHUNK_SIZE
                num_chunks = (len(df) + chunk_size - 1) // chunk_size
                
                for i in range(num_chunks):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(df))
                    chunk = df.iloc[start_idx:end_idx]
                    
                    logger.info(f"Processing chunk {i+1}/{num_chunks} with {len(chunk)} rows")
                    self.processing_status.current_chunk = i + 1
                    
                    # Validate chunk
                    success, errors = self.validate_data(chunk)
                    if not success:
                        yield False, "\n".join(errors)
                        return
                        
                    # Save chunk
                    success, message = self.save_data(chunk, user_id)
                    if not success:
                        yield False, message
                        return
                        
                    self.processing_status.processed_rows += len(chunk)
                    yield True, f"Processed {self.processing_status.processed_rows} rows"
                
            except pd.errors.EmptyDataError:
                logger.error("CSV file is empty")
                yield False, "CSV file is empty"
            except Exception as e:
                logger.error(f"Error reading CSV with pandas: {str(e)}")
                yield False, f"Error reading CSV file: {str(e)}"
                
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            yield False, f"Error processing file: {str(e)}"
            
    def _detect_file_encoding(self, file_path: str) -> str:
        """
        Dosyanın encoding'ini tespit et ve gerekirse dönüştür.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            str: Tespit edilen encoding
        """
        import chardet
        
        # Önce dosyanın encoding'ini tespit et
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            detected_encoding = result['encoding']
            
        logger.info(f"Detected encoding: {detected_encoding}")
        
        # Eğer UTF-8 değilse, dosyayı UTF-8'e dönüştür
        if detected_encoding and detected_encoding.lower() != 'utf-8':
            try:
                # Orijinal içeriği oku
                with open(file_path, 'r', encoding=detected_encoding) as file:
                    content = file.read()
                    
                # UTF-8 olarak kaydet
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    
                logger.info(f"Converted file from {detected_encoding} to UTF-8")
                return 'utf-8'
            except Exception as e:
                logger.warning(f"Error converting encoding: {str(e)}")
                # Hata durumunda orijinal encoding'i kullan
                return detected_encoding or 'utf-8'
        
        return detected_encoding or 'utf-8'
            
    def _handle_error(self, error_msg: str) -> Tuple[bool, str]:
        """Handle processing error."""
        self.processing_status.status = "failed"
        self.processing_status.errors.append(error_msg)
        logger.error(f"Processing error: {error_msg}")
        return False, error_msg
        
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        return self.processing_status.to_dict()

    def validate_store_access(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Validate that the user has access to the stores in the CSV."""
        try:
            if 'store_id' not in df.columns:
                return False, "CSV file does not contain store_id column"
                
            store_ids = df['store_id'].unique()
            user_stores = Store.query.filter(
                Store.id.in_(store_ids),
                Store.user_id == user_id
            ).all()
            
            if len(user_stores) != len(store_ids):
                return False, "User does not have access to all stores in the CSV"
                
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating store access: {str(e)}")
            return False, f"Error validating store access: {str(e)}"

    @abstractmethod
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the processed data to the database."""
        pass