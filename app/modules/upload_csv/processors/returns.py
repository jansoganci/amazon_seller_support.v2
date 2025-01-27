"""Returns CSV processor module."""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging

from app import db
from app.modules.returns.models import ReturnReport
from app.modules.returns.constants import (
    REQUIRED_COLUMNS, ERROR_MESSAGES,
    VALID_RETURN_CENTERS, VALID_RETURN_CARRIERS,
    VALID_TRACKING_PREFIXES
)
from .base import BaseCSVProcessor
from ..validators.returns import ReturnCSVValidator

logger = logging.getLogger(__name__)

# CSV template definitions - order is important
RETURN_REPORT_COLUMNS = {
    'store_id': {'type': int, 'required': True, 'description': 'Store ID'},
    'return_date': {'type': 'date', 'required': True, 'format': '%Y-%m-%d', 'description': 'Return date (YYYY-MM-DD)'},
    'order_id': {'type': str, 'required': True, 'description': 'Order ID'},
    'sku': {'type': str, 'required': True, 'description': 'Product SKU'},
    'asin': {'type': str, 'required': True, 'description': 'Amazon ASIN'},
    'title': {'type': str, 'required': True, 'description': 'Product title'},
    'quantity': {'type': int, 'required': True, 'description': 'Return quantity'},
    'return_reason': {'type': str, 'required': True, 'description': 'Return reason'},
    'status': {'type': str, 'required': True, 'description': 'Return status'},
    'refund_amount': {'type': float, 'required': True, 'description': 'Refund amount'},
    'return_center': {'type': str, 'required': True, 'description': 'Return center'},
    'return_carrier': {'type': str, 'required': True, 'description': 'Return carrier'},
    'tracking_number': {'type': str, 'required': True, 'description': 'Tracking number'}
}

class ReturnCSVProcessor(BaseCSVProcessor):
    """CSV processor for return reports."""
    
    def __init__(self):
        """Initialize the return CSV processor."""
        super().__init__(report_type='return_report')
        self.validator = ReturnCSVValidator()
        
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate CSV data against the template.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, List[str]]: (success status, list of error messages)
        """
        errors = []
        
        # Column validation - order is important
        expected_columns = list(RETURN_REPORT_COLUMNS.keys())
        if list(df.columns) != expected_columns:
            errors.append(f"Columns must be in the specified order: {', '.join(expected_columns)}")
            return False, errors
            
        # Data type and format validation
        for col, specs in RETURN_REPORT_COLUMNS.items():
            # Required field validation
            if specs['required']:
                if df[col].isnull().any():
                    errors.append(f"{specs['description']} cannot be empty")
                    
            # Data type validation
            try:
                if specs['type'] == int:
                    df[col] = df[col].astype(int)
                elif specs['type'] == float:
                    df[col] = df[col].astype(float)
                elif specs['type'] == 'date':
                    df[col] = pd.to_datetime(df[col], format=specs['format']).dt.date
                elif specs['type'] == str:
                    df[col] = df[col].astype(str)
            except Exception as e:
                errors.append(f"Invalid value for {specs['description']}: {str(e)}")
                
        # Business rule validation
        # Date validation
        if 'return_date' in df.columns:
            current_date = datetime.now().date()
            try:
                future_dates = df['return_date'].apply(lambda x: x > current_date if pd.notna(x) else False)
                if future_dates.any():
                    errors.append("Future dates are not allowed")
            except Exception as e:
                errors.append(f"Error during date comparison: {str(e)}")
                
        # Numeric field validation
        if 'quantity' in df.columns:
            invalid_quantities = df['quantity'] <= 0
            if invalid_quantities.any():
                errors.append("Quantity must be greater than 0")
                
        if 'refund_amount' in df.columns:
            invalid_amounts = df['refund_amount'] < 0
            if invalid_amounts.any():
                errors.append("Refund amount cannot be negative")
                
        # Status validation
        if 'status' in df.columns:
            valid_statuses = ['Pending', 'Approved', 'Rejected', 'Completed']
            invalid_statuses = ~df['status'].isin(valid_statuses)
            if invalid_statuses.any():
                errors.append(f"Invalid status. Valid values: {', '.join(valid_statuses)}")

        # Return center validation
        if 'return_center' in df.columns:
            invalid_centers = ~df['return_center'].isin(VALID_RETURN_CENTERS)
            if invalid_centers.any():
                errors.append(ERROR_MESSAGES['INVALID_RETURN_CENTER'])

        # Return carrier validation
        if 'return_carrier' in df.columns:
            invalid_carriers = ~df['return_carrier'].isin(VALID_RETURN_CARRIERS)
            if invalid_carriers.any():
                errors.append(ERROR_MESSAGES['INVALID_RETURN_CARRIER'])

        # Tracking number validation
        if 'tracking_number' in df.columns:
            invalid_tracking = []
            for idx, tracking in enumerate(df['tracking_number'], 1):
                tracking_str = str(tracking)
                if not any(tracking_str.startswith(prefix) for prefix in VALID_TRACKING_PREFIXES):
                    invalid_tracking.append(idx)
            
            if invalid_tracking:
                errors.append(ERROR_MESSAGES['INVALID_TRACKING_NUMBER'])

        return len(errors) == 0, errors
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the return report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            # Validate data first
            is_valid, errors = self.validate_data(df)
            if not is_valid:
                return False, "\n".join(errors)
            
            # Define unique columns for return reports
            unique_columns = ['store_id', 'return_date', 'order_id', 'sku']
            
            for _, row in df.iterrows():
                # Create a filter dictionary based on unique columns
                filters = {col: row[col] for col in unique_columns}
                existing_record = ReturnReport.query.filter_by(**filters).first()
                
                # CSV'den gelen sütunların modeldeki alanlarla eşleştiğinden emin ol
                report_data = {col: row[col] for col in RETURN_REPORT_COLUMNS.keys()}
                
                if existing_record:
                    # Update existing record
                    for key, value in report_data.items():
                        setattr(existing_record, key, value)
                    records_updated += 1
                else:
                    # Create new record
                    new_record = ReturnReport(**report_data)
                    db.session.add(new_record)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving return report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"
            
    def get_template(self) -> Dict[str, Any]:
        """Get the CSV template definition.
        
        Returns:
            Dict[str, Any]: Template definition including columns and their specifications
        """
        return {
            'name': 'Return Report',
            'description': 'Amazon Return Report CSV template',
            'columns': RETURN_REPORT_COLUMNS,
            'sample_row': {
                'store_id': '1',
                'return_date': '2025-01-01',
                'order_id': '123-4567890-1234567',
                'sku': 'ABC123',
                'asin': 'B0123456789',
                'title': 'Test Product',
                'quantity': '1',
                'return_reason': 'Damaged Product',
                'status': 'Completed',
                'refund_amount': '99.99',
                'return_center': 'ABC Returns Center',
                'return_carrier': 'XYZ Shipping',
                'tracking_number': 'TR123456789'
            }
        }