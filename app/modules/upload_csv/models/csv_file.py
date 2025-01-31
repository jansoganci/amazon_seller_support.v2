"""CSV file model."""
from datetime import datetime, UTC
from typing import Optional, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

class CSVFile(db.Model):
    """CSV file model for tracking uploaded files."""
    __tablename__ = 'csv_files'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    store_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    filename: Mapped[str] = mapped_column(db.String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(db.String(50), nullable=False)  # business_report, inventory_report, etc.
    file_size: Mapped[int] = mapped_column(db.Integer, nullable=False)  # in bytes
    file_path: Mapped[str] = mapped_column(db.String(512), nullable=False)  # physical path on disk
    row_count: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)  # number of rows in CSV
    processed_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime, nullable=True)  # when the file was processed
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="csv_files", lazy=True)
    store: Mapped["Store"] = relationship("Store", back_populates="csv_files", lazy=True)
    upload_history: Mapped[Optional["UploadHistory"]] = relationship("UploadHistory", back_populates="csv_file", uselist=False)

    __table_args__ = (
        db.Index('idx_csv_files_user_store', 'user_id', 'store_id'),  # For faster user+store queries
        db.Index('idx_csv_files_type_date', 'file_type', 'created_at'),  # For report type filtering
    )

    def __repr__(self) -> str:
        """String representation."""
        return f'<CSVFile {self.filename} ({self.file_type})>'

    def to_dict(self) -> dict:
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
            'updated_at': self.updated_at.isoformat()
        }