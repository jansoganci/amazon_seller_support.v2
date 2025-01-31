"""Store models for Amazon Seller Support."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

class Store(db.Model):
    """Store model for managing Amazon seller stores.
    
    This model represents an Amazon seller store and manages its relationships
    with users and various reports (business, inventory, etc.).
    
    Attributes:
        id: Primary key
        name: Store name (e.g., "My Amazon Store")
        marketplace: Amazon marketplace (e.g., "US", "UK", etc.)
        user_id: Foreign key to User model
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        owner: Relationship to User model
        business_reports: Relationship to BusinessReport model
        advertising_reports: Relationship to AdvertisingReport model
        inventory_reports: Relationship to InventoryReport model
        return_reports: Relationship to ReturnReport model
        csv_files: Relationship to CSVFile model
    """
    __tablename__ = 'stores'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    marketplace: Mapped[str] = mapped_column(db.String(50), nullable=False)  # US, UK, etc.
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="stores", foreign_keys=[user_id])
    business_reports: Mapped[List["BusinessReport"]] = relationship("BusinessReport", back_populates="store", lazy=True)
    advertising_reports: Mapped[List["AdvertisingReport"]] = relationship("AdvertisingReport", back_populates="store", lazy=True)
    inventory_reports: Mapped[List["InventoryReport"]] = relationship("InventoryReport", back_populates="store", lazy=True)
    return_reports: Mapped[List["ReturnReport"]] = relationship("ReturnReport", back_populates="store", lazy=True)
    csv_files: Mapped[List["CSVFile"]] = relationship("CSVFile", back_populates="store", lazy=True)

    def __repr__(self) -> str:
        return f"<Store {self.name} ({self.marketplace})>"