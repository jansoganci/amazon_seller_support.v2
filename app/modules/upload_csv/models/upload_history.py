"""Upload history model."""
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

class UploadHistory(db.Model):
    """Upload history model for tracking CSV file processing status."""
    __tablename__ = 'upload_history'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    csv_file_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('csv_files.id'), nullable=False)
    status: Mapped[str] = mapped_column(db.String(20), nullable=False)  # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    rows_processed: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    csv_file: Mapped["CSVFile"] = relationship("CSVFile", back_populates="upload_history")

    def __repr__(self) -> str:
        """String representation."""
        return f'<UploadHistory {self.csv_file_id} ({self.status})>'

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'csv_file_id': self.csv_file_id,
            'status': self.status,
            'error_message': self.error_message,
            'rows_processed': self.rows_processed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
