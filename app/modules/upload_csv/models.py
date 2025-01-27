"""
CSV file and upload history models.
"""

from app.extensions import db
from datetime import datetime, UTC

class CSVFile(db.Model):
    """CSV file model for tracking uploaded files."""
    __tablename__ = 'csv_files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # business_report, inventory_report, etc.
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_path = db.Column(db.String(512), nullable=False)  # physical path on disk
    row_count = db.Column(db.Integer, nullable=True)  # number of rows in CSV
    processed_at = db.Column(db.DateTime, nullable=True)  # when the file was processed
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    user = db.relationship('User', back_populates='csv_files')
    store = db.relationship('Store', back_populates='csv_files')
    upload_history = db.relationship('UploadHistory', back_populates='csv_file', uselist=False)

    __table_args__ = (
        db.Index('idx_csv_files_user_store', 'user_id', 'store_id'),  # For faster user+store queries
        db.Index('idx_csv_files_type_date', 'file_type', 'created_at'),  # For report type filtering
    )

    def __repr__(self):
        """String representation."""
        return f'<CSVFile {self.filename} ({self.file_type})>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'store_id': self.store_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'row_count': self.row_count,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,  # Include status in dictionary
            'error_message': self.error_message  # Include error message in dictionary
        }

    @property
    def status(self):
        """Get file processing status with detailed information."""
        if not self.upload_history:
            return {
                'code': 'pending',
                'description': 'The file is waiting to be processed.'
            }
        
        status_map = {
            'pending': {
                'code': 'pending',
                'description': 'The file is waiting to be processed.'
            },
            'processing': {
                'code': 'processing',
                'description': 'The file is currently being processed.'
            },
            'success': {
                'code': 'success',
                'description': 'The file has been processed successfully.'
            },
            'error': {
                'code': 'error',
                'description': 'An error occurred while processing the file.'
            }
        }
        
        return status_map.get(self.upload_history.status, {
            'code': 'unknown',
            'description': 'The status of the file is unknown.'
        })

    @property
    def error_message(self):
        """Get detailed error message if any."""
        if not self.upload_history or self.upload_history.status != 'error':
            return None
        
        return {
            'message': self.upload_history.message,
            'timestamp': self.upload_history.created_at.isoformat(),
            'details': {
                'file_type': self.file_type,
                'row_count': self.row_count,
                'processed_at': self.processed_at.isoformat() if self.processed_at else None
            }
        }