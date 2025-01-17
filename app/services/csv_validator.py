from flask_login import current_user

import pandas as pd
import numpy as np
from decimal import Decimal
import io
from app import db
from app.models.store import Store
from app.models.reports import BusinessReport, AdvertisingReport, ReturnReport, InventoryReport

import logging
logger = logging.getLogger(__name__)

class CSVValidator:
    # CSV dosya tipleri ve zorunlu sütunları
    REQUIRED_COLUMNS = {
        'store': ['store_id', 'store_name', 'store_region'],
        'business_report': [
            'store_id', 'date', 'sku', 'asin', 'title', 
            'sessions', 'units_ordered', 'ordered_product_sales', 
            'total_order_items', 'conversion_rate'
        ],
        'advertising_report': [
            'store_id', 'date', 'campaign_name', 'ad_group_name', 
            'targeting_type', 'match_type', 'search_term', 
            'impressions', 'clicks', 'ctr', 'cpc', 'spend', 
            'total_sales', 'acos', 'total_orders', 'total_units', 
            'conversion_rate'
        ],
        'return_report': [
            'store_id', 'return_date', 'order_id', 'sku', 'asin', 'title',
            'quantity', 'return_reason', 'status', 'refund_amount',
            'return_center', 'return_carrier', 'tracking_number'
        ],
        'inventory_report': [
            'store_id', 'date', 'sku', 'asin', 'product_name', 
            'condition', 'price', 'mfn_listing_exists', 
            'mfn_fulfillable_quantity', 'afn_listing_exists', 
            'afn_warehouse_quantity', 'afn_fulfillable_quantity', 
            'afn_unsellable_quantity', 'afn_reserved_quantity', 
            'afn_total_quantity', 'per_unit_volume'
        ]
    }

    # Sayısal sütunlar ve tipleri
    NUMERIC_COLUMNS = {
        'store': {},
        'business_report': {
            'units_ordered': int,
            'ordered_product_sales': Decimal,
            'sessions': int,
            'total_order_items': int,
            'conversion_rate': Decimal
        },
        'advertising_report': {
            'impressions': int,
            'clicks': int,
            'ctr': Decimal,
            'cpc': Decimal,
            'spend': Decimal,
            'total_sales': Decimal,
            'acos': Decimal,
            'total_orders': int,
            'total_units': int,
            'conversion_rate': Decimal
        },
        'return_report': {
            'store_id': int,
            'quantity': int,
            'refund_amount': Decimal
        },
        'inventory_report': {
            'price': Decimal,
            'mfn_fulfillable_quantity': int,
            'afn_warehouse_quantity': int,
            'afn_fulfillable_quantity': int,
            'afn_unsellable_quantity': int,
            'afn_reserved_quantity': int,
            'afn_total_quantity': int,
            'per_unit_volume': Decimal
        }
    }

    # Boolean sütunlar
    BOOLEAN_COLUMNS = {
        'store': {},
        'business_report': {},
        'advertising_report': {},
        'return_report': {},
        'inventory_report': {
            'mfn_listing_exists': ['true', 'false', '1', '0', 'yes', 'no'],
            'afn_listing_exists': ['true', 'false', '1', '0', 'yes', 'no']
        }
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
        """CSV verilerini doğrula ve dönüştür"""
        try:
            # Boolean alanları dönüştür
            if report_type in CSVValidator.BOOLEAN_COLUMNS:
                for col, valid_values in CSVValidator.BOOLEAN_COLUMNS[report_type].items():
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: CSVValidator.convert_to_boolean(x, valid_values))
            
            # Tarih alanını dönüştür
            if 'date' in df.columns:
                try:
                    df['date'] = pd.to_datetime(df['date']).dt.date
                except Exception as e:
                    return False, f"Geçersiz tarih formatı: {str(e)}", None
            
            # Sayısal alanları dönüştür
            if report_type in CSVValidator.NUMERIC_COLUMNS:
                for col, type_info in CSVValidator.NUMERIC_COLUMNS[report_type].items():
                    if col in df.columns:
                        if type_info == int:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                        elif type_info == Decimal:
                            df[col] = df[col].apply(lambda x: CSVValidator.convert_to_decimal(x))
            
            return True, "Veri doğrulama başarılı", df
            
        except Exception as e:
            return False, f"Veri doğrulama hatası: {str(e)}", None

    @staticmethod
    def validate_csv(file, report_type):
        """CSV dosyasını doğrula ve dönüştür"""
        try:
            logger.info(f"CSV validasyonu başlıyor - Dosya tipi: {report_type}")
            
            # Dosya içeriğini oku
            file_content = file.read()
            logger.info(f"Dosya içeriği okundu: {len(file_content)} bytes")
            file.seek(0)
            
            logger.info("Pandas ile CSV okuma başlıyor")
            df = pd.read_csv(file)
            logger.info(f"DataFrame oluşturuldu. Sütunlar: {df.columns.tolist()}")
            logger.info(f"Satır sayısı: {len(df)}")
            
            # Zorunlu sütunları kontrol et
            required_columns = CSVValidator.REQUIRED_COLUMNS[report_type]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Eksik sütunlar: {', '.join(missing_columns)}"
                logger.error(error_msg)
                return False, error_msg, None
            logger.info("Zorunlu sütun kontrolü başarılı")
            
            # Store ID'leri kontrol et
            store_ids = df['store_id'].unique()
            logger.info(f"Store ID'ler: {store_ids}")
            
            # DataFrame sütunlarını logla
            logger.info(f"DataFrame sütunları: {df.columns.tolist()}")
            
            # Giriş yapan kullanıcıyı logla
            logger.info(f"Giriş yapan kullanıcı ID: {current_user.id}")
            
            # Kullanıcının store'larını kontrol et
            user_stores = Store.query.filter_by(user_id=current_user.id).all()
            user_store_ids = [store.id for store in user_stores]
            logger.info(f"Kullanıcının mağazaları: {user_store_ids}")
            logger.info(f"CSV'deki mağaza ID'leri: {store_ids.tolist()}")
            
            # Veri dönüştürme
            logger.info("Veri dönüştürme başlıyor")
            
            # Return report için tarih dönüşümü
            if report_type == 'return_report':
                df['return_date'] = pd.to_datetime(df['return_date']).dt.date
            
            logger.info("Veri dönüştürme başarılı")
            
            metadata = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'file_type': report_type,
                'store_ids': store_ids.tolist(),
                'transformed_data': df
            }
            
            logger.info(f"Validasyon başarılı. Metadata: {metadata}")
            return True, "CSV doğrulama başarılı", metadata

        except Exception as e:
            error_msg = f"CSV doğrulama hatası: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
