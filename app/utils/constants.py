"""Amazon kategori sabitleri."""
import json
import os

AMAZON_CATEGORIES = {
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

def load_asin_categories():
    """ASIN-kategori eşleştirmelerini JSON dosyasından yükler."""
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'asin_categories.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# ASIN kategorilerini yükle
ASIN_CATEGORIES = load_asin_categories()

def get_category_by_asin(asin: str) -> tuple[str, str]:
    """
    ASIN'e göre kategori ve alt kategori kodunu döndürür.
    
    Args:
        asin (str): Amazon ASIN kodu
        
    Returns:
        tuple[str, str]: (ana_kategori_kodu, alt_kategori_kodu)
    """
    # ASIN kategorilerden bul
    asin_data = ASIN_CATEGORIES.get(asin, None)
    
    if asin_data:
        main_cat = asin_data['main_category']
        sub_cat = asin_data['sub_category']
        return (main_cat, sub_cat)
    
    # ASIN bulunamazsa None döndür
    return None 

# Error messages
ERROR_MESSAGES = {
    'INVALID_DATE': 'Invalid date format. Expected format: YYYY-MM-DD',
    'INVALID_NUMBER': '{} must be a valid number',
    'INVALID_DECIMAL': '{} must be a valid decimal number',
    'INVALID_STORE': 'Invalid store ID',
    'UNAUTHORIZED': 'User is not authorized to access this store',
    'FILE_EMPTY': 'The uploaded file is empty',
    'MISSING_COLUMNS': 'Missing required columns in the file',
    'DUPLICATE_ROWS': 'Duplicate entries found in the file',
    'UNKNOWN_ERROR': 'An unknown error occurred'
}

# ASIN Categories
ASIN_CATEGORIES = {
    'Electronics': ['B00', 'B01'],
    'Home & Kitchen': ['B02', 'B03'],
    'Sports & Outdoors': ['B04', 'B05'],
    'Beauty & Personal Care': ['B06', 'B07'],
    'Toys & Games': ['B08', 'B09']
}

def get_category_by_asin(asin: str) -> tuple:
    """Get category and subcategory for an ASIN."""
    prefix = asin[:3] if asin else ''
    for category, prefixes in ASIN_CATEGORIES.items():
        if prefix in prefixes:
            return category, None
    return 'Other', None 