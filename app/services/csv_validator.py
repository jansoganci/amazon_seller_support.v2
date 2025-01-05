import pandas as pd
import numpy as np
from decimal import Decimal
import io
from app import db
from app.models.store import Store
from app.models.reports import BusinessReport, AdvertisingReport, ReturnReport, InventoryReport

class CSVValidator:
    # CSV dosya tipleri ve zorunlu sütunları
    REQUIRED_COLUMNS = {
        'store': ['store_id', 'store_name', 'store_region'],
        'business_report': ['store_id', 'asin', 'title', 'units_sold', 'revenue', 'returns', 'conversion_rate', 'page_views', 'sessions'],
        'advertising_report': ['store_id', 'store_name', 'campaign_name', 'impressions', 'clicks', 'cost', 'sales', 'acos', 'roi'],
        'return_report': ['store_id', 'store_name', 'asin', 'title', 'return_reason', 'return_count', 'total_units_sold', 'return_rate', 'customer_feedback'],
        'inventory_report': ['store_id', 'store_name', 'asin', 'title', 'units_available', 'units_inbound', 'units_reserved', 'units_total', 'reorder_required']
    }

    # Sayısal sütunlar ve tipleri
    NUMERIC_COLUMNS = {
        'store': {},
        'business_report': {
            'units_sold': int,
            'revenue': Decimal,
            'returns': int,
            'conversion_rate': Decimal,
            'page_views': int,
            'sessions': int
        },
        'advertising_report': {
            'impressions': int,
            'clicks': int,
            'cost': Decimal,
            'sales': Decimal,
            'acos': Decimal,
            'roi': Decimal
        },
        'return_report': {
            'return_count': int,
            'total_units_sold': int,
            'return_rate': Decimal
        },
        'inventory_report': {
            'units_available': int,
            'units_inbound': int,
            'units_reserved': int,
            'units_total': int
        }
    }

    # Boolean sütunlar
    BOOLEAN_COLUMNS = {
        'store': {},
        'business_report': {},
        'advertising_report': {},
        'return_report': {},
        'inventory_report': {'reorder_required': ['true', 'false', '1', '0', 'yes', 'no']}
    }

    @staticmethod
    def convert_to_decimal(value):
        """String'i Decimal'e çevirir"""
        try:
            # Yüzde işareti varsa kaldır
            if isinstance(value, str):
                value = value.replace('%', '').strip()
            return Decimal(str(value))
        except Exception as e:
            raise ValueError(f"Geçersiz sayısal değer: {value}")

    @staticmethod
    def convert_to_boolean(value, valid_values):
        """String'i boolean'a çevirir"""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ['true', '1', 'yes', 'y']:
                return True
            if value in ['false', '0', 'no', 'n']:
                return False
        raise ValueError(f"Geçersiz boolean değer: {value}")

    @staticmethod
    def validate_and_transform_data(df, report_type):
        """DataFrame'deki verileri doğrular ve dönüştürür"""
        try:
            # Sayısal sütunları dönüştür
            for column, type_ in CSVValidator.NUMERIC_COLUMNS[report_type].items():
                if column not in df.columns:
                    continue
                    
                try:
                    if type_ == Decimal:
                        df[column] = df[column].apply(CSVValidator.convert_to_decimal)
                    else:
                        df[column] = df[column].astype(type_)
                except Exception as e:
                    return False, f"Geçersiz sayısal değer tespit edildi: {str(e)}", None

            # Boolean sütunları dönüştür
            for column, valid_values in CSVValidator.BOOLEAN_COLUMNS[report_type].items():
                if column not in df.columns:
                    continue
                    
                try:
                    df[column] = df[column].apply(lambda x: CSVValidator.convert_to_boolean(x, valid_values))
                except Exception as e:
                    return False, f"Geçersiz boolean değer tespit edildi: {str(e)}", None

            return True, "", df

        except Exception as e:
            return False, f"Veri dönüştürme hatası: {str(e)}", None

    @staticmethod
    def validate_csv(file, report_type):
        """CSV dosyasını doğrular ve metadata bilgisini döndürür"""
        try:
            # Dosya tipini kontrol et
            if report_type not in CSVValidator.REQUIRED_COLUMNS:
                return False, f"Geçersiz dosya tipi: {report_type}", {}

            # CSV'yi oku
            try:
                # Dosya tipine göre okuma yöntemini belirle
                if isinstance(file, io.StringIO):
                    content = file.getvalue()
                else:
                    content = file.read().decode('utf-8')
                
                # Eğer içerik boşsa
                if not content.strip():
                    return False, "CSV dosyası boş", {}
                
                # StringIO kullanarak pandas'a ver
                file = io.StringIO(content)
                
                # CSV'yi oku
                df = pd.read_csv(file, skipinitialspace=True)
                
            except pd.errors.EmptyDataError:
                return False, "CSV dosyası boş", {}
            except Exception as e:
                return False, f"CSV okuma hatası: {str(e)}", {}
            
            # Boş dosya kontrolü
            if df.empty:
                return False, "CSV dosyası boş", {}
            
            # Boş satır kontrolü
            if df.isna().any().any():
                return False, "Boş satır tespit edildi", {}
            
            # Zorunlu sütunları kontrol et
            required_columns = CSVValidator.REQUIRED_COLUMNS[report_type]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Eksik zorunlu sütunlar: {', '.join(missing_columns)}", {}
            
            # Store ID kontrolü (rapor dosyaları için)
            if report_type != 'store':
                # Store ID'leri integer'a çevir
                try:
                    df['store_id'] = df['store_id'].astype(int)
                except Exception:
                    return False, "Geçersiz store_id değerleri tespit edildi", {}
                    
                store_ids = df['store_id'].unique()
                existing_stores = Store.query.filter(Store.id.in_(store_ids)).all()
                existing_store_ids = [store.id for store in existing_stores]
                missing_store_ids = [str(id) for id in store_ids if id not in existing_store_ids]
                
                if missing_store_ids:
                    return False, f"Bazı mağazalar sistemde bulunamadı: {', '.join(missing_store_ids)}", {}

            # Verileri doğrula ve dönüştür
            is_valid, error_message, transformed_df = CSVValidator.validate_and_transform_data(df, report_type)
            if not is_valid:
                return False, error_message, {}

            # Metadata bilgisini hazırla
            metadata = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'file_type': report_type,
                'store_ids': df['store_id'].unique().tolist(),
                'transformed_data': transformed_df
            }
            
            return True, "CSV dosyası başarıyla doğrulandı", metadata
            
        except Exception as e:
            return False, f"CSV doğrulama hatası: {str(e)}", {}
