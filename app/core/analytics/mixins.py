"""Mixins for analytics engines."""

from typing import Dict, List, Optional, Union
from datetime import datetime

from sqlalchemy import and_
from app.core.models.base_report import BaseReport

class CategoryAwareMixin:
    """Mixin to add category-aware functionality to analytics engines.
    
    This mixin provides methods for:
    - Filtering data by category
    - Calculating category-specific metrics
    - Comparing categories
    """
    
    def filter_by_category(
        self,
        data: List[Dict],
        category_id: Optional[int] = None,
        subcategory_id: Optional[int] = None
    ) -> List[Dict]:
        """Filter data by category and/or subcategory.
        
        Args:
            data: List of data points to filter
            category_id: Main category ID (optional)
            subcategory_id: Subcategory ID (optional)
            
        Returns:
            Filtered list of data points
        """
        if not category_id and not subcategory_id:
            return data
            
        return [
            item for item in data
            if (not category_id or item.get('category_id') == category_id) and
               (not subcategory_id or item.get('subcategory_id') == subcategory_id)
        ]
    
    def get_category_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        category_id: Optional[int] = None
    ) -> Dict:
        """Get metrics for specific category.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            category_id: Category ID to analyze (optional)
            
        Returns:
            Dict containing category metrics
        """
        # Get base data
        data = self._get_data(start_date, end_date)
        
        # Apply category filter if needed
        if category_id:
            data = self.filter_by_category(data, category_id=category_id)
            
        # Calculate metrics
        return self.calculate_base_metrics(data, self.get_category_metric_list())
    
    def compare_categories(
        self,
        start_date: datetime,
        end_date: datetime,
        category_ids: List[int]
    ) -> Dict:
        """Compare metrics across different categories.
        
        Args:
            start_date: Start date for comparison
            end_date: End date for comparison
            category_ids: List of category IDs to compare
            
        Returns:
            Dict containing comparison data
        """
        result = {}
        for category_id in category_ids:
            result[category_id] = self.get_category_metrics(
                start_date,
                end_date,
                category_id
            )
        return result
    
    def get_category_metric_list(self) -> List[str]:
        """Get list of metrics to calculate for categories.
        
        This should be implemented by each analytics engine to specify
        which metrics are relevant for category analysis.
        
        Returns:
            List of metric IDs
        """
        return []  # Override in specific analytics engine
