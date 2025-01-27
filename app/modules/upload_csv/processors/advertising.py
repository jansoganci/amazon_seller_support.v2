"""Advertising CSV processor module."""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging

from app import db
from app.modules.advertising.models import AdvertisingReport
from app.modules.advertising.constants import REQUIRED_COLUMNS, ERROR_MESSAGES
from .base import BaseCSVProcessor
from ..validators.advertising import AdvertisingCSVValidator

logger = logging.getLogger(__name__)

# CSV şablon tanımları - sıralama önemli
ADVERTISING_REPORT_COLUMNS = {
    'store_id': {'type': int, 'required': True, 'description': 'Mağaza ID'},
    'date': {'type': 'date', 'required': True, 'format': '%Y-%m-%d', 'description': 'Rapor tarihi (YYYY-MM-DD)'},
    'campaign_name': {'type': str, 'required': True, 'description': 'Kampanya adı'},
    'ad_group_name': {'type': str, 'required': True, 'description': 'Reklam grubu adı'},
    'targeting_type': {'type': str, 'required': True, 'description': 'Hedefleme tipi'},
    'match_type': {'type': str, 'required': True, 'description': 'Eşleşme tipi'},
    'search_term': {'type': str, 'required': True, 'description': 'Arama terimi'},
    'impressions': {'type': int, 'required': True, 'description': 'Gösterim sayısı'},
    'clicks': {'type': int, 'required': True, 'description': 'Tıklama sayısı'},
    'ctr': {'type': float, 'required': True, 'description': 'Tıklama oranı'},
    'cpc': {'type': float, 'required': True, 'description': 'Tıklama başı maliyet'},
    'spend': {'type': float, 'required': True, 'description': 'Toplam harcama'},
    'total_sales': {'type': float, 'required': True, 'description': 'Toplam satış'},
    'acos': {'type': float, 'required': True, 'description': 'Reklam maliyeti/satış oranı'},
    'total_orders': {'type': int, 'required': True, 'description': 'Toplam sipariş sayısı'},
    'total_units': {'type': int, 'required': True, 'description': 'Toplam ürün adedi'},
    'conversion_rate': {'type': float, 'required': True, 'description': 'Dönüşüm oranı'}
}

class AdvertisingCSVProcessor(BaseCSVProcessor):
    """CSV processor for advertising reports."""
    
    def __init__(self):
        """Initialize the advertising CSV processor."""
        super().__init__(report_type='advertising_report')
        self.validator = AdvertisingCSVValidator()
        
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate CSV data against the template.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, List[str]]: (success status, list of error messages)
        """
        errors = []
        
        # Sütun kontrolü - sıra önemli
        expected_columns = list(ADVERTISING_REPORT_COLUMNS.keys())
        if list(df.columns) != expected_columns:
            errors.append(f"Sütunlar belirtilen sırada olmalıdır: {', '.join(expected_columns)}")
            return False, errors
            
        # Veri tipi ve format kontrolü
        for col, specs in ADVERTISING_REPORT_COLUMNS.items():
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
                current_date = pd.Timestamp(datetime.now().date())
                future_dates = df['date'].dt.date > current_date.date()
                if future_dates.any():
                    errors.append("Gelecek tarihli kayıtlar olamaz")
            except Exception as e:
                errors.append(f"Tarih karşılaştırmasında hata: {str(e)}")
                
        # Sayısal alan kontrolleri
        if 'ctr' in df.columns:
            invalid_rates = (df['ctr'] < 0) | (df['ctr'] > 100)
            if invalid_rates.any():
                errors.append("CTR oranı 0 ile 100 arasında olmalıdır")
                
        if 'conversion_rate' in df.columns:
            invalid_rates = (df['conversion_rate'] < 0) | (df['conversion_rate'] > 1)
            if invalid_rates.any():
                errors.append("Dönüşüm oranı 0 ile 1 arasında olmalıdır")
                
        if 'acos' in df.columns:
            invalid_acos = df['acos'] < 0
            if invalid_acos.any():
                errors.append("ACoS negatif olamaz")
                
        # Mantıksal kontroller
        if all(col in df.columns for col in ['clicks', 'impressions']):
            invalid_clicks = df['clicks'] > df['impressions']
            if invalid_clicks.any():
                errors.append("Tıklama sayısı gösterim sayısından büyük olamaz")
                
        if all(col in df.columns for col in ['total_units', 'total_orders']):
            invalid_units = df['total_units'] < df['total_orders']
            if invalid_units.any():
                errors.append("Toplam ürün adedi sipariş sayısından küçük olamaz")
                
        return len(errors) == 0, errors
        
    def save_data(self, df: pd.DataFrame, user_id: int) -> Tuple[bool, str]:
        """Save the advertising report data to the database."""
        try:
            records_processed = 0
            records_updated = 0
            
            # Validate data first
            is_valid, errors = self.validate_data(df)
            if not is_valid:
                return False, "\n".join(errors)
            
            # Define unique columns for advertising reports
            unique_columns = ['store_id', 'date', 'campaign_name', 'ad_group_name', 'targeting_type', 'search_term']
            
            for _, row in df.iterrows():
                # Create a filter dictionary based on unique columns
                filters = {col: row[col] for col in unique_columns}
                existing_record = AdvertisingReport.query.filter_by(**filters).first()
                
                # CSV'den gelen sütunların modeldeki alanlarla eşleştiğinden emin ol
                report_data = {col: row[col] for col in ADVERTISING_REPORT_COLUMNS.keys()}
                
                if existing_record:
                    # Update existing record
                    for key, value in report_data.items():
                        setattr(existing_record, key, value)
                    records_updated += 1
                else:
                    # Create new record
                    new_record = AdvertisingReport(**report_data)
                    db.session.add(new_record)
                    records_processed += 1
                    
            db.session.commit()
            return True, f"Processed {records_processed} new records and updated {records_updated} records"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving advertising report data: {str(e)}")
            return False, f"Error saving data: {str(e)}"
            
    def get_template(self) -> Dict[str, Any]:
        """Get the CSV template definition.
        
        Returns:
            Dict[str, Any]: Template definition including columns and their specifications
        """
        return {
            'name': 'Advertising Report',
            'description': 'Amazon Advertising raporu için CSV şablonu',
            'columns': ADVERTISING_REPORT_COLUMNS,
            'sample_row': {
                'store_id': '1',
                'date': '2025-01-01',
                'campaign_name': 'Test Campaign',
                'ad_group_name': 'Test Ad Group',
                'targeting_type': 'AUTO',
                'match_type': 'BROAD',
                'search_term': 'test product',
                'impressions': '1000',
                'clicks': '100',
                'ctr': '10.0',
                'cpc': '0.50',
                'spend': '50.00',
                'total_sales': '200.00',
                'acos': '25.0',
                'total_orders': '10',
                'total_units': '15',
                'conversion_rate': '0.10'
            }
        }