"""CSV processor for business reports."""

import pandas as pd
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any

from app.modules.business.models import BusinessReport
from app.core.models.store import Store
from app.extensions import db

class BusinessCSVProcessor:
    """Process business report CSV files."""
    
    def __init__(self, file_path: str, store: Store):
        """Initialize processor.
        
        Args:
            file_path: Path to CSV file
            store: Store instance
        """
        self.file_path = file_path
        self.store = store
        self.required_columns = {
            'Date': str,
            'ASIN': str,
            'Title': str,
            'Category': str,
            'Subcategory': str,
            'Ordered Product Sales': float,
            'Units Ordered': int,
            'Sessions': int,
            'Page Views': int,
            'Buy Box Percentage': float,
            'Units Ordered - B2B': int,
            'Ordered Product Sales - B2B': float
        }

    def process(self) -> List[BusinessReport]:
        """Process CSV file and create business reports.
        
        Returns:
            List of created BusinessReport instances
        """
        # Read CSV file
        df = pd.read_csv(self.file_path)
        
        # Validate columns
        self._validate_columns(df)
        
        # Process each row
        reports = []
        for _, row in df.iterrows():
            report = BusinessReport(
                store_id=self.store.id,
                date=datetime.strptime(row['Date'], '%Y-%m-%d').date(),
                asin=row['ASIN'],
                title=row['Title'],
                category=row['Category'],
                subcategory=row['Subcategory'],
                ordered_product_sales=Decimal(str(row['Ordered Product Sales'])),
                units_ordered=row['Units Ordered'],
                sessions=row['Sessions'],
                page_views=row['Page Views'],
                buy_box_percentage=Decimal(str(row['Buy Box Percentage'])),
                units_ordered_b2b=row['Units Ordered - B2B'],
                ordered_product_sales_b2b=Decimal(str(row['Ordered Product Sales - B2B']))
            )
            reports.append(report)
            
        # Save to database
        db.session.bulk_save_objects(reports)
        db.session.commit()
        
        return reports
        
    def _validate_columns(self, df: pd.DataFrame) -> None:
        """Validate CSV columns.
        
        Args:
            df: Pandas DataFrame
            
        Raises:
            ValueError: If required columns are missing or have wrong data type
        """
        missing_columns = set(self.required_columns.keys()) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
        for col, dtype in self.required_columns.items():
            try:
                df[col].astype(dtype)
            except (ValueError, TypeError):
                raise ValueError(f"Column '{col}' has invalid data type. Expected {dtype.__name__}")
