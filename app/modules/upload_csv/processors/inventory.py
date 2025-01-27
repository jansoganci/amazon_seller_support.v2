"""Inventory CSV processor module."""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging

from app import db
from app.modules.inventory.models import InventoryReport
from app.modules.inventory.constants import REQUIRED_COLUMNS, ERROR_MESSAGES
from .base import BaseCSVProcessor
from ..validators.inventory import InventoryCSVValidator

logger = logging.getLogger(__name__)

# CSV şablon tanımları - sıralama önemli
INVENTORY_REPORT_COLUMNS = {
    'store_id': {'type': int, 'required': True, 'description': 'Mağaza ID'},
    'date': {'type': 'date', 'required': True, 'format': '%Y-%m-%d', 'description': 'Rapor tarihi (YYYY-MM-DD)'},
    'sku': {'type': str, 'required': True, 'description': 'Ürün SKU kodu'},
    'asin': {'type': str, 'required': True, 'description': 'Amazon ASIN numarası'},
    'product_name': {'type': str, 'required': True, 'description': 'Ürün adı'},
    'condition': {'type': str, 'required': True, 'description': 'Ürün durumu'},
    'price': {'type': float, 'required': True, 'description': 'Ürün fiyatı'},
    'mfn_listing_exists': {'type': bool, 'required': True, 'description': 'MFN listesi var mı'},
    'mfn_fulfillable_quantity': {'type': int, 'required': True, 'description': 'MFN gönderilebilir miktar'},
    'afn_listing_exists': {'type': bool, 'required': True, 'description': 'AFN listesi var mı'},
    'afn_warehouse_quantity': {'type': int, 'required': True, 'description': 'AFN depo miktarı'},
    'afn_fulfillable_quantity': {'type': int, 'required': True, 'description': 'AFN gönderilebilir miktar'},
    'afn_unsellable_quantity': {'type': int, 'required': True, 'description': 'AFN satılamaz miktar'},
    'afn_reserved_quantity': {'type': int, 'required': True, 'description': 'AFN rezerve miktar'},
    'afn_total_quantity': {'type': int, 'required': True, 'description': 'AFN toplam miktar'},
    'per_unit_volume': {'type': float, 'required': True, 'description': 'Birim başına hacim'}
}

class InventoryCSVProcessor(BaseCSVProcessor):
    """CSV processor for inventory reports."""
    
    def __init__(self):
        """Initialize the inventory CSV processor."""
        super().__init__(report_type='inventory_report')
        self.validator = InventoryCSVValidator()
        
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate CSV data against the template.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, List[str]]: (success status, list of error messages)
        """
        errors = []
        
        # Sütun kontrolü - sıra önemli
        expected_columns = list(INVENTORY_REPORT_COLUMNS.keys())
        if list(df.columns) != expected_columns:
            errors.append(f"Sütunlar belirtilen sırada olmalıdır: {', '.join(expected_columns)}")
            return False, errors
            
        # Veri tipi ve format kontrolü
        for col, specs in INVENTORY_REPORT_COLUMNS.items():
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
                elif specs['type'] == bool:
                    df[col] = df[col].astype(bool)
                elif specs['type'] == 'date':
                    try:
                        df[col] = pd.to_datetime(df[col], format=specs['format']).dt.date
                    except (ValueError, TypeError) as e:
                        errors.append(f"{specs['description']} için geçersiz değer: {str(e)}")
                        continue
                elif specs['type'] == str:
                    df[col] = df[col].astype(str)
            except Exception as e:
                errors.append(f"{specs['description']} için geçersiz değer: {str(e)}")
                
        if len(errors) > 0:
            return False, errors
                
        # İş kuralları kontrolü
        # Tarih kontrolü
        if 'date' in df.columns and not df['date'].isnull().any():
            current_date = datetime.now().date()
            future_dates = df['date'].apply(lambda x: x > current_date)
            if future_dates.any():
                errors.append("Gelecek tarihli kayıtlar olamaz")
                
        # Sayısal alan kontrolleri
        if 'price' in df.columns:
            invalid_prices = df['price'] < 0
            if invalid_prices.any():
                errors.append("Ürün fiyatı negatif olamaz")
                
        if 'per_unit_volume' in df.columns:
            invalid_volumes = df['per_unit_volume'] <= 0
            if invalid_volumes.any():
                errors.append("Birim hacim 0'dan büyük olmalıdır")
                
        # AFN miktar kontrolleri
        quantity_columns = [
            'afn_warehouse_quantity',
            'afn_fulfillable_quantity',
            'afn_unsellable_quantity',
            'afn_reserved_quantity'
        ]
        
        for col in quantity_columns:
            if col in df.columns:
                invalid_quantities = df[col] < 0
                if invalid_quantities.any():
                    errors.append(f"{INVENTORY_REPORT_COLUMNS[col]['description']} negatif olamaz")
                    
        # Toplam miktar kontrolü
        if all(col in df.columns for col in quantity_columns + ['afn_total_quantity']):
            calculated_total = (
                df['afn_warehouse_quantity'] +
                df['afn_fulfillable_quantity'] +
                df['afn_unsellable_quantity'] +
                df['afn_reserved_quantity']
            )
            invalid_totals = df['afn_total_quantity'] != calculated_total
            if invalid_totals.any():
                errors.append("AFN toplam miktar, diğer AFN miktarların toplamına eşit olmalıdır")
                
        return len(errors) == 0, errors
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the inventory report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            # Validate data first
            is_valid, errors = self.validate_data(df)
            if not is_valid:
                return False, "\n".join(errors)
            
            # Define unique columns for inventory reports
            unique_columns = ['store_id', 'date', 'sku', 'asin']
            
            for _, row in df.iterrows():
                # Create a filter dictionary based on unique columns
                filters = {col: row[col] for col in unique_columns}
                existing_record = InventoryReport.query.filter_by(**filters).first()
                
                # CSV'den gelen sütunların modeldeki alanlarla eşleştiğinden emin ol
                report_data = {col: row[col] for col in INVENTORY_REPORT_COLUMNS.keys()}
                
                if existing_record:
                    # Update existing record
                    for key, value in report_data.items():
                        setattr(existing_record, key, value)
                    records_updated += 1
                else:
                    # Create new record
                    new_record = InventoryReport(**report_data)
                    db.session.add(new_record)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving inventory report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"
            
    def get_template(self) -> Dict[str, Any]:
        """Get the CSV template definition.
        
        Returns:
            Dict[str, Any]: Template definition including columns and their specifications
        """
        return {
            'name': 'Inventory Report',
            'description': 'Amazon Inventory raporu için CSV şablonu',
            'columns': INVENTORY_REPORT_COLUMNS,
            'sample_row': {
                'store_id': '1',
                'date': '2025-01-01',
                'sku': 'ABC123',
                'asin': 'B0123456789',
                'product_name': 'Test Ürün',
                'condition': 'New',
                'price': '99.99',
                'mfn_listing_exists': 'True',
                'mfn_fulfillable_quantity': '10',
                'afn_listing_exists': 'True',
                'afn_warehouse_quantity': '50',
                'afn_fulfillable_quantity': '45',
                'afn_unsellable_quantity': '2',
                'afn_reserved_quantity': '3',
                'afn_total_quantity': '100',
                'per_unit_volume': '1.5'
            }
        }