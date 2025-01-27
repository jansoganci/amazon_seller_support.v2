"""
CSV processors for different report types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Generator
import pandas as pd
from werkzeug.datastructures import FileStorage
from flask import current_app
import os
import logging
from datetime import datetime
import json

from app import db
from app.models.store import Store
from app.modules.business.models import BusinessReport
from app.modules.advertising.models import AdvertisingReport
from app.modules.inventory.models import InventoryReport
from app.modules.returns.models import ReturnReport
from .validators import CSVValidator
from .constants import CSV_COLUMNS, ERROR_MESSAGES
from .utils import (
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
        self.validator = CSVValidator()
        self.processing_status = ProcessingStatus()
        
    def process_file(self, file: FileStorage, user_id: int) -> Tuple[bool, str]:
        """Process the uploaded CSV file."""
        try:
            # Reset processing status
            self.processing_status = ProcessingStatus()
            self.processing_status.status = "processing"
            
            # Step 1: Validate file size and type
            is_valid, error_msg = validate_file_size(file)
            if not is_valid:
                return self._handle_error(error_msg)
                
            is_valid, error_msg = validate_file_type(file)
            if not is_valid:
                return self._handle_error(error_msg)
            
            # Step 2: Create necessary folders
            try:
                upload_path, temp_path = create_upload_folders(user_id, self.report_type)
            except FileValidationError as e:
                return self._handle_error(str(e))
            
            # Step 3: Save file with safe name
            safe_filename = generate_safe_filename(file.filename, user_id)
            temp_file_path = os.path.join(temp_path, safe_filename)
            file.save(temp_file_path)
            
            # Step 4: Process file in chunks
            success = True
            message = ""
            try:
                # Count total rows first
                self.processing_status.total_rows = sum(1 for _ in pd.read_csv(temp_file_path, chunksize=1))
                
                # Process in chunks
                for success, message in self._process_chunks(temp_file_path, user_id):
                    if not success:
                        break
                
                if success:
                    # Move file to final location if processing successful
                    final_path = os.path.join(upload_path, safe_filename)
                    os.rename(temp_file_path, final_path)
                    
                    # Calculate and store file hash
                    file_hash = get_file_hash(final_path)
                    if file_hash:
                        # TODO: Store file hash in database
                        pass
                    
            finally:
                # Cleanup temp file if it still exists
                cleanup_temp_files(temp_file_path)
            
            self.processing_status.status = "completed" if success else "failed"
            return success, message
            
        except Exception as e:
            logger.error(f"Error processing {self.report_type} CSV: {str(e)}")
            return self._handle_error(f"Error processing file: {str(e)}")
            
    def _process_chunks(self, file_path: str, user_id: int) -> Generator[Tuple[bool, str], None, None]:
        """Process file in chunks."""
        try:
            chunks = pd.read_csv(file_path, chunksize=CHUNK_SIZE)
            for chunk_num, chunk_df in enumerate(chunks, 1):
                self.processing_status.current_chunk = chunk_num
                
                # Validate chunk structure and data
                is_valid, errors = self.validator.validate_csv(chunk_df, self.report_type)
                if not is_valid:
                    yield False, "\n".join(errors)
                    return
                
                # Validate store access for chunk
                is_valid, error_msg = self.validate_store_access(chunk_df, user_id)
                if not is_valid:
                    yield False, error_msg
                    return
                
                # Process chunk data
                success, message = self.save_data(chunk_df, user_id)
                if not success:
                    yield False, message
                    return
                
                # Update progress
                self.processing_status.processed_rows += len(chunk_df)
                
                yield True, "Chunk processed successfully"
                
            yield True, f"Processed {self.processing_status.processed_rows} rows successfully"
            
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            yield False, f"Error processing chunk: {str(e)}"
            
    def _handle_error(self, error_msg: str) -> Tuple[bool, str]:
        """Handle processing error."""
        self.processing_status.status = "failed"
        self.processing_status.errors.append(error_msg)
        logger.error(f"Processing error: {error_msg}")
        return False, error_msg
        
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        return self.processing_status.to_dict()

    @abstractmethod
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the processed data to the database."""
        pass

    def validate_store_access(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Validate that the user has access to the stores in the CSV."""
        try:
            store_ids = df['store_id'].unique()
            user_stores = Store.query.filter_by(user_id=user_id).all()
            user_store_ids = [store.id for store in user_stores]
            
            unauthorized_stores = [
                str(store_id) for store_id in store_ids 
                if store_id not in user_store_ids
            ]
            
            if unauthorized_stores:
                return False, ERROR_MESSAGES['store_not_found'].format(
                    ', '.join(unauthorized_stores)
                )
                
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating store access: {str(e)}")
            return False, f"Error validating store access: {str(e)}"


class BusinessCSVProcessor(BaseCSVProcessor):
    """CSV processor for business reports."""
    
    def __init__(self):
        """Initialize the business CSV processor."""
        super().__init__(report_type='business_report')
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the business report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            for _, row in df.iterrows():
                existing_report = BusinessReport.query.filter_by(
                    store_id=row['store_id'],
                    date=row['date'],
                    asin=row['asin']
                ).first()
                
                if existing_report:
                    # Update existing record
                    existing_report.sku = row['sku']
                    existing_report.title = row['title']
                    existing_report.sessions = row['sessions']
                    existing_report.units_ordered = row['units_ordered']
                    existing_report.ordered_product_sales = row['ordered_product_sales']
                    existing_report.total_order_items = row['total_order_items']
                    existing_report.conversion_rate = row['conversion_rate']
                    records_updated += 1
                else:
                    # Create new record
                    new_report = BusinessReport(
                        store_id=row['store_id'],
                        date=row['date'],
                        sku=row['sku'],
                        asin=row['asin'],
                        title=row['title'],
                        sessions=row['sessions'],
                        units_ordered=row['units_ordered'],
                        ordered_product_sales=row['ordered_product_sales'],
                        total_order_items=row['total_order_items'],
                        conversion_rate=row['conversion_rate']
                    )
                    db.session.add(new_report)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving business report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"


class AdvertisingCSVProcessor(BaseCSVProcessor):
    """CSV processor for advertising reports."""
    
    def __init__(self):
        """Initialize the advertising CSV processor."""
        super().__init__(report_type='advertising_report')
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the advertising report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            for _, row in df.iterrows():
                existing_report = AdvertisingReport.query.filter_by(
                    store_id=row['store_id'],
                    date=row['date'],
                    campaign_name=row['campaign_name'],
                    ad_group_name=row['ad_group_name']
                ).first()
                
                if existing_report:
                    # Update existing record
                    for col in self.required_columns:
                        setattr(existing_report, col, row[col])
                    records_updated += 1
                else:
                    # Create new record
                    new_report = AdvertisingReport(**row.to_dict())
                    db.session.add(new_report)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving advertising report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"


class InventoryCSVProcessor(BaseCSVProcessor):
    """CSV processor for inventory reports."""
    
    def __init__(self):
        """Initialize the inventory CSV processor."""
        super().__init__(report_type='inventory_report')
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the inventory report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            for _, row in df.iterrows():
                existing_report = InventoryReport.query.filter_by(
                    store_id=row['store_id'],
                    date=row['date'],
                    sku=row['sku']
                ).first()
                
                if existing_report:
                    # Update existing record
                    for col in self.required_columns:
                        setattr(existing_report, col, row[col])
                    records_updated += 1
                else:
                    # Create new record
                    new_report = InventoryReport(**row.to_dict())
                    db.session.add(new_report)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving inventory report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"


class ReturnCSVProcessor(BaseCSVProcessor):
    """CSV processor for return reports."""
    
    def __init__(self):
        """Initialize the return CSV processor."""
        super().__init__(report_type='return_report')
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the return report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            for _, row in df.iterrows():
                existing_report = ReturnReport.query.filter_by(
                    store_id=row['store_id'],
                    return_date=row['return_date'],
                    order_id=row['order_id']
                ).first()
                
                if existing_report:
                    # Update existing record
                    for col in self.required_columns:
                        setattr(existing_report, col, row[col])
                    records_updated += 1
                else:
                    # Create new record
                    new_report = ReturnReport(**row.to_dict())
                    db.session.add(new_report)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving return report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"