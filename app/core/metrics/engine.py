"""
Metric Engine - Core component for metric calculations and management.
"""
from typing import Any, Dict, List, Optional, Union
import operator
import re
from functools import reduce
from datetime import datetime, timedelta
import pandas as pd
from app.core.cache import cache
from decimal import Decimal

class MetricEngine:
    """Metric calculation engine."""
    
    def __init__(self):
        """Initialize metric engine."""
        self._metrics: Dict[str, Dict] = {}
        self._operators = {
            'sum': lambda x: sum(x),
            'avg': lambda x: sum(x) / len(x) if x else 0,
            'count': lambda x: len([v for v in x if v]),
            'min': lambda x: min(x) if x else 0,
            'max': lambda x: max(x) if x else 0
        }
        
    def register_metric(self, metric_config: Dict[str, Any]) -> None:
        """Register a new metric configuration."""
        metric_id = metric_config['id']
        if metric_id in self._metrics:
            raise ValueError(f"Metric {metric_id} already registered")
        
        # Validate required fields
        required_fields = ['id', 'name', 'formula', 'category', 'visualization']
        missing_fields = [f for f in required_fields if f not in metric_config]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
        self._metrics[metric_id] = metric_config
        
    def calculate_metric(self, metric_id: str, data: List[Dict], context: Optional[Dict] = None) -> str:
        """Calculate a metric value."""
        if metric_id not in self._metrics:
            raise ValueError(f"Unknown metric: {metric_id}")
            
        metric = self._metrics[metric_id]
        
        # Try to get from cache first
        if metric.get('caching'):
            cache_key = self._build_cache_key(metric_id, data, context)
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
                
        # Calculate raw value
        if callable(metric['formula']):
            value = metric['formula'](data, context)
        else:
            value = self._calculate_raw_value(metric, data)
            
        # Format value
        formatted_value = self._format_value(value, metric['visualization'])
        
        # Cache result if needed
        if metric.get('caching'):
            cache_key = self._build_cache_key(metric_id, data, context)
            cache.set(cache_key, formatted_value, ttl=metric['caching'].get('duration'))
            
        return formatted_value
        
    def calculate_metrics(self, metric_ids: List[str], data: List[Dict], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Calculate multiple metrics at once."""
        return {
            metric_id: self.calculate_metric(metric_id, data, context)
            for metric_id in metric_ids
        }
    
    def get_metric_config(self, metric_id: str) -> Dict:
        """Get metric configuration."""
        if metric_id not in self._metrics:
            raise ValueError(f"Unknown metric: {metric_id}")
        return self._metrics[metric_id]
    
    def _parse_value(self, value: Union[str, int, float, Decimal]) -> float:
        """Parse a value to float."""
        # Handle numeric types directly
        if isinstance(value, (int, float)):
            return float(value)
            
        if isinstance(value, Decimal):
            return float(value)
            
        # Handle string values
        if isinstance(value, str):
            # Remove currency symbols and commas
            value = value.replace('$', '').replace(',', '').replace('%', '')
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Cannot parse string value: {value}")
            
        # Handle None or other types
        if value is None:
            return 0.0
            
        raise ValueError(f"Cannot parse value of type {type(value)}")
        
    def _calculate_raw_value(self, metric: Dict, data: List[Dict]) -> Union[int, float, str]:
        """Calculate raw metric value."""
        if not data:
            return 0
            
        formula = metric['formula']
        # Parse formula and extract operations
        operations = re.findall(r'(\w+)\(([\w_]+)\)', formula)
        
        if not operations:
            raise ValueError(f"Invalid formula format: {formula}")
            
        results = {}
        for op, field in operations:
            if op not in self._operators:
                raise ValueError(f"Unknown operator: {op}")
                
            values = [self._parse_value(d.get(field, 0)) for d in data]
            if not values:
                values = [0]
            results[f"{op}({field})"] = self._operators[op](values)
            
        # Replace operations with values in formula
        result_formula = formula
        for op_str, value in results.items():
            result_formula = result_formula.replace(op_str, str(value))
            
        return eval(result_formula)
        
    def _format_value(self, value: Union[int, float, str], visualization: Dict) -> str:
        """Format a value according to visualization settings."""
        if value is None or (isinstance(value, (int, float)) and value == 0):
            if visualization['type'] == 'currency':
                return '$0.00'
            elif visualization['type'] == 'percentage':
                return '0.00%'
            elif visualization['type'] == 'number':
                return '0'
            else:
                return str(value)
                
        try:
            value = self._parse_value(value)
        except (TypeError, ValueError):
            return str(value)
            
        if visualization['type'] == 'currency':
            return f"${value:,.2f}"
        elif visualization['type'] == 'percentage':
            return f"{value:.2f}%"
        elif visualization['type'] == 'number':
            return f"{int(value):,}" if value.is_integer() else f"{value:,.2f}"
        else:
            return str(value)
            
    def evaluate_thresholds(self, metric_id: str, value: Union[str, int, float]) -> str:
        """Evaluate thresholds for a metric value."""
        if metric_id not in self._metrics:
            raise ValueError(f"Unknown metric: {metric_id}")
            
        metric = self._metrics[metric_id]
        thresholds = metric.get('thresholds', {})
        
        if not thresholds:
            return 'normal'
            
        try:
            value = self._parse_value(value)
            critical = self._parse_value(thresholds.get('critical', float('-inf')))
            warning = self._parse_value(thresholds.get('warning', float('-inf')))
        except (TypeError, ValueError):
            return 'normal'
            
        direction = thresholds.get('direction', 'desc')
        
        if direction == 'desc':
            if value <= critical:
                return 'critical'
            elif value <= warning:
                return 'warning'
        else:  # asc
            if value >= critical:
                return 'critical'
            elif value >= warning:
                return 'warning'
                
        return 'normal'
        
    def _build_cache_key(self, metric_id: str, data: List[Dict], context: Optional[Dict]) -> str:
        """Build a cache key for a metric calculation."""
        metric = self._metrics[metric_id]
        cache_config = metric.get('caching', {})
        
        key_parts = [metric_id]
        if cache_config.get('key'):
            for key_field in cache_config['key']:
                if context and key_field in context:
                    key_parts.append(f"{key_field}:{context[key_field]}")
                    
        return ':'.join(key_parts)

# Global metric engine instance
metric_engine = MetricEngine()
