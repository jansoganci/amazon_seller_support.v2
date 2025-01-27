"""Advertising CSV validator."""

from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd

from app.core.csv.exceptions import (
    CSVError,
    EmptyDataFrameError,
    MissingColumnsError,
    DuplicateEntriesError,
    InvalidDataError,
    InvalidStoreError,
    UnauthorizedError
)
from app.models.store import Store
from app.modules.advertising.models import AdvertisingReport
from app.core.csv.validator import BaseCSVValidator
from app.utils.constants import ERROR_MESSAGES

class AdvertisingCSVValidator(BaseCSVValidator):
    """Advertising CSV validator."""

    REQUIRED_COLUMNS = [
        'date',
        'campaign_name',
        'campaign_id',
        'impressions',
        'clicks',
        'spend',
        'sales',
        'orders',
        'units'
    ]

    def __init__(self, user_id: int = None, store_id: int = None):
        """Initialize validator with user and store IDs."""
        super().__init__(user_id, store_id)
        self.model = AdvertisingReport

    def validate_file(self, df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """Validate the uploaded file."""
        try:
            # Check if DataFrame is empty
            if df.empty:
                raise EmptyDataFrameError()

            # Check for required columns
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                raise MissingColumnsError(missing_columns)

            # Check for duplicate entries
            duplicates = df.duplicated(subset=['date', 'campaign_id'], keep=False)
            if duplicates.any():
                duplicate_rows = df[duplicates].index.tolist()
                raise DuplicateEntriesError(duplicate_rows)

            return True, None

        except CSVError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def validate_store_access(self, store_id: int) -> Tuple[bool, Optional[str]]:
        """Validate user's access to the store."""
        try:
            # Check if store exists
            store = Store.query.get(store_id)
            if not store:
                raise InvalidStoreError()

            # Check if user has access to store
            if not any(s.id == store_id for s in self.user.stores):
                raise UnauthorizedError()

            return True, None

        except CSVError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """Validate the data in the DataFrame."""
        try:
            # Validate date format
            for idx, date_str in enumerate(df['date']):
                try:
                    datetime.strptime(str(date_str), '%Y-%m-%d')
                except ValueError:
                    raise InvalidDataError(f"Row {idx + 1}: {ERROR_MESSAGES['INVALID_DATE']}")

            # Validate numeric fields
            numeric_fields = {
                'impressions': int,
                'clicks': int,
                'spend': float,
                'sales': float,
                'orders': int,
                'units': int
            }

            for field, field_type in numeric_fields.items():
                for idx, value in enumerate(df[field]):
                    try:
                        converted_value = field_type(value)
                        if converted_value < 0:
                            raise ValueError()
                    except (ValueError, TypeError):
                        raise InvalidDataError(
                            f"Row {idx + 1}: {ERROR_MESSAGES['INVALID_NUMBER'].format(field)}"
                        )

            return True, None

        except CSVError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e) 