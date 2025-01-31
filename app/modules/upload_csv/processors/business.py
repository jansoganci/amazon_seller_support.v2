"""Business CSV processor module."""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging

from app import db
from app.modules.business.models import BusinessReport
from app.modules.business.constants import REQUIRED_COLUMNS, ERROR_MESSAGES
from .base import BaseCSVProcessor
from ..validators.business import BusinessCSVValidator
from app.modules.stores.models import Store  # Store modülünün doğru path'i

logger = logging.getLogger(__name__)

# CSV şablon tanımları
BUSINESS_REPORT_COLUMNS = {
    'store_id': {'type': int, 'required': True, 'description': 'Mağaza ID'},
    'date': {'type': 'date', 'required': True, 'format': '%Y-%m-%d', 'description': 'Rapor tarihi (YYYY-MM-DD)'},
    'sku': {'type': str, 'required': True, 'description': 'Ürün SKU kodu'},
    'asin': {'type': str, 'required': True, 'description': 'Amazon ASIN numarası'},
    'title': {'type': str, 'required': True, 'description': 'Ürün başlığı'},
    'sessions': {'type': int, 'required': True, 'description': 'Toplam oturum sayısı'},
    'units_ordered': {'type': int, 'required': True, 'description': 'Sipariş edilen ürün adedi'},
    'ordered_product_sales': {'type': float, 'required': True, 'description': 'Toplam satış tutarı'},
    'total_order_items': {'type': int, 'required': True, 'description': 'Toplam sipariş kalemi'},
    'conversion_rate': {'type': float, 'required': True, 'description': 'Dönüşüm oranı'}
}

class BusinessCSVProcessor(BaseCSVProcessor):
    """CSV processor for business reports."""
    
    def __init__(self):
        """Initialize the business CSV processor."""
        super().__init__(report_type='business_report')
        self.validator = BusinessCSVValidator()
        
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate CSV data against the template.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, List[str]]: (success status, list of error messages)
        """
        errors = []
        
        # Sütun kontrolü
        missing_columns = [col for col in BUSINESS_REPORT_COLUMNS if col not in df.columns]
        if missing_columns:
            errors.append(f"Eksik sütunlar: {', '.join(missing_columns)}")
            return False, errors
            
        # Veri tipi ve format kontrolü
        for col, specs in BUSINESS_REPORT_COLUMNS.items():
            # Boş değer kontrolü
            if specs['required']:
                if df[col].isnull().any():
                    errors.append(f"{specs['description']} boş olamaz")
                    
            # Veri tipi kontrolü
            try:
                if specs['type'] == int:
                    df[col] = df[col].astype(int)
                elif specs['type'] == float:
                    df[col] = df[col].astype(float)
                elif specs['type'] == 'date':
                    df[col] = pd.to_datetime(df[col], format=specs['format'])
                elif specs['type'] == str:
                    df[col] = df[col].astype(str)
            except Exception as e:
                errors.append(f"{specs['description']} için geçersiz değer: {str(e)}")
                
        # İş kuralları kontrolü
        # Tarih kontrolü
        if 'date' in df.columns:
            try:
                df['date'] = pd.to_datetime(df['date'])
                current_date = pd.Timestamp(datetime.now().date())
                future_dates = df['date'].dt.date > current_date.date()
                if future_dates.any():
                    errors.append("Gelecek tarihli kayıtlar olamaz")
            except Exception as e:
                errors.append(f"Geçersiz tarih formatı: {str(e)}")
                
        # Sayısal alan kontrolleri
        if 'units_ordered' in df.columns and 'total_order_items' in df.columns:
            invalid_orders = df['units_ordered'] > df['total_order_items']
            if invalid_orders.any():
                errors.append("Sipariş edilen ürün adedi toplam sipariş kaleminden büyük olamaz")
                
        if 'conversion_rate' in df.columns:
            invalid_rates = (df['conversion_rate'] < 0) | (df['conversion_rate'] > 1)
            if invalid_rates.any():
                errors.append("Dönüşüm oranı 0 ile 1 arasında olmalıdır")
                
        return len(errors) == 0, errors
        
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
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the business report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            # Validate data first
            is_valid, errors = self.validate_data(df)
            if not is_valid:
                return False, "\n".join(errors)
            
            # Validate store access
            for _, row in df.iterrows():
                is_valid, errors = self.validate_store_access(row['store_id'], user_id)
                if not is_valid:
                    return False, "\n".join(errors)
            
            # Define unique columns for business reports
            unique_columns = ['store_id', 'date', 'sku', 'asin']
            
            for _, row in df.iterrows():
                # Create a filter dictionary based on unique columns
                filters = {col: row[col] for col in unique_columns}
                existing_record = BusinessReport.query.filter_by(**filters).first()
                
                # CSV'den gelen sütunların modeldeki alanlarla eşleştiğinden emin ol
                report_data = {
                    'store_id': row['store_id'],
                    'date': row['date'],
                    'sku': row['sku'],
                    'asin': row['asin'],
                    'title': row['title'],
                    'sessions': row['sessions'],
                    'units_ordered': row['units_ordered'],
                    'ordered_product_sales': row['ordered_product_sales'],
                    'total_order_items': row['total_order_items'],
                    'conversion_rate': row['conversion_rate']
                }
                
                if existing_record:
                    # Update existing record
                    for key, value in report_data.items():
                        setattr(existing_record, key, value)
                    records_updated += 1
                else:
                    # Create new record
                    new_record = BusinessReport(**report_data)
                    db.session.add(new_record)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving business report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"
            
    def get_template(self) -> Dict[str, Any]:
        """Get the CSV template definition.
        
        Returns:
            Dict[str, Any]: Template definition including columns and their specifications
        """
        return {
            'name': 'Business Report',
            'description': 'Amazon Business raporu için CSV şablonu',
            'columns': BUSINESS_REPORT_COLUMNS,
            'sample_row': {
                'store_id': '1',
                'date': '2025-01-01',
                'sku': 'ABC123',
                'asin': 'B0123456789',
                'title': 'Örnek Ürün',
                'sessions': '100',
                'units_ordered': '10',
                'ordered_product_sales': '1000.50',
                'total_order_items': '15',
                'conversion_rate': '0.15'
            }
        }
        
    def export_data(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Export business report data.
        
        Args:
            store_id: Store ID to export data for
            start_date: Start date of export range
            end_date: End date of export range
            
        Returns:
            Tuple[bool, str, Optional[pd.DataFrame]]: (success status, message, exported data)
        """
        try:
            # Get reports for date range
            reports = BusinessReport.query.filter(
                BusinessReport.store_id == store_id,
                BusinessReport.date.between(start_date, end_date)
            ).order_by(BusinessReport.date).all()
            
            if not reports:
                return False, ERROR_MESSAGES['NO_DATA'], None
                
            # Convert to DataFrame
            data = [report.to_dict() for report in reports]
            df = pd.DataFrame(data)
            
            return True, f"Successfully exported {len(reports)} records", df
            
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            return False, f"Export error: {str(e)}", None