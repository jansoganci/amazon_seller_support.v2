"""Amazon kategori sabitleri ve yardımcı fonksiyonları."""

import json
import os
from typing import Dict, Tuple, Optional

class AmazonCategories:
    """Amazon kategori sabitleri."""
    
    CATEGORIES = {
        'FASHION': {
            'code': 'FSH',
            'subcategories': {
                'SUNGLASSES': 'SGL',
                'WATCHES': 'WTC',
                'APPAREL': 'APR',
                'SHOES': 'SHO',
                'JEWELLRY': 'JWL',
                'BAGS_LUGGAGE': 'BAG',
                'HANDBAGS': 'HBG',
                'KIDS_APPAREL': 'KAP'
            }
        },
        'DAILY_ESSENTIALS': {
            'code': 'DES',
            'subcategories': {
                'HPC': 'HPC',
                'TOYS': 'TOY',
                'PETS': 'PET',
                'GROCERY': 'GRO',
                'BABY': 'BAB',
                'BEAUTY': 'BTY',
                'COMBO_OFFERS': 'CMB',
                'PHARMACY': 'PHR'
            }
        },
        'HOME_KITCHEN_OUTDOORS': {
            'code': 'HKO',
            'subcategories': {
                'HOME': 'HOM',
                'KITCHEN': 'KIT',
                'SPORTS': 'SPT',
                'AUTOMOTIVE': 'AUT',
                'INDUSTRIAL_SCIENTIFIC': 'IND',
                'HOME_IMPROVEMENT': 'HIM',
                'LAWN_GARDEN': 'LWG',
                'FURNITURE': 'FUR'
            }
        },
        'ELECTRONICS': {
            'code': 'ELE',
            'subcategories': {
                'ALL_ELECTRONICS': 'AEL',
                'TV': 'TEL',
                'PC': 'COM',
                'CAMERA': 'CAM',
                'SMALL_APPLIANCES': 'SAP',
                'MUSICAL_INSTRUMENTS': 'MUS',
                'PCA': 'PCA',
                'STATIONERY': 'STN',
                'TV_APPLIANCES': 'TVA'
            }
        },
        'BOOKS_ENTERTAINMENT': {
            'code': 'BKE',
            'subcategories': {
                'BOOKS': 'BOK',
                'VIDEO_GAMES': 'VGM',
                'MOVIES': 'MOV'
            }
        },
        'AMAZON_INITIATIVES': {
            'code': 'AMZ',
            'subcategories': {
                'LAUNCHPAD': 'LPD',
                'SNS': 'SNS',
                'PB': 'PBR',
                'KARIGOR': 'KAR'
            }
        }
    }

    @classmethod
    def get_category_codes(cls, main_category: str) -> Optional[Dict[str, str]]:
        """Ana kategori için kod ve alt kategori kodlarını döndürür."""
        category = cls.CATEGORIES.get(main_category)
        if not category:
            return None
        return {
            'main_code': category['code'],
            'subcategories': category['subcategories']
        }

    @classmethod
    def get_all_category_codes(cls) -> Dict[str, str]:
        """Tüm kategori kodlarını düz bir dictionary olarak döndürür."""
        codes = {}
        for main_cat, data in cls.CATEGORIES.items():
            codes[main_cat] = data['code']
            for sub_cat, sub_code in data['subcategories'].items():
                codes[f"{main_cat}_{sub_cat}"] = sub_code
        return codes

    @classmethod
    def validate_category(cls, main_category: str, sub_category: str = None) -> bool:
        """Kategori ve alt kategori kombinasyonunun geçerli olup olmadığını kontrol eder."""
        if main_category not in cls.CATEGORIES:
            return False
        
        if sub_category:
            return sub_category in cls.CATEGORIES[main_category]['subcategories']
        
        return True

class CategoryManager:
    """ASIN-kategori eşleştirmelerini yöneten sınıf."""
    
    def __init__(self):
        self._asin_categories = self._load_asin_categories()

    def _load_asin_categories(self) -> Dict[str, Dict[str, str]]:
        """ASIN-kategori eşleştirmelerini JSON dosyasından yükler."""
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'asin_categories.json')
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_category_by_asin(self, asin: str) -> Optional[Tuple[str, str]]:
        """ASIN'e göre kategori ve alt kategori kodunu döndürür."""
        asin_data = self._asin_categories.get(asin)
        if not asin_data:
            return None

        main_cat = asin_data['main_category']
        sub_cat = asin_data['sub_category']

        category_data = AmazonCategories.get_category_codes(main_cat)
        if not category_data:
            return None

        return (
            category_data['main_code'],
            category_data['subcategories'].get(sub_cat)
        )

    def update_asin_category(self, asin: str, main_category: str, sub_category: str) -> bool:
        """ASIN için kategori bilgisini günceller."""
        if not AmazonCategories.validate_category(main_category, sub_category):
            return False

        self._asin_categories[asin] = {
            'main_category': main_category,
            'sub_category': sub_category
        }
        return True 