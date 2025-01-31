"""Models package."""

# Import db instance first
from app.extensions import db

# Import all models
from app.modules.auth.models import User
from app.modules.stores.models import Store
from app.modules.business.models import BusinessReport
from app.modules.category.models import Category, ASINCategory
from app.modules.advertising.models import AdvertisingReport
from app.modules.inventory.models import InventoryReport
from app.modules.returns.models import ReturnReport
from app.modules.upload_csv.models import CSVFile

# Register all models
__all__ = [
    'db',
    'User',
    'Store',
    'CSVFile',
    'BusinessReport',
    'AdvertisingReport',
    'InventoryReport',
    'ReturnReport',
    'Category',
    'ASINCategory'
]

# Ensure all models are loaded
db.Model.metadata.tables
