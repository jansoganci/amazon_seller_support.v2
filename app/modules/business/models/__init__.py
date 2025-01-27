"""Business module models."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.store import Store

class BusinessReport(db.Model):
    """Business report model."""
    __tablename__ = "business_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=False)
    asin: Mapped[str] = mapped_column(db.String(20), nullable=False)
    sessions: Mapped[int] = mapped_column(default=0)
    session_percentage: Mapped[float] = mapped_column(default=0.0)
    page_views: Mapped[int] = mapped_column(default=0)
    page_views_percentage: Mapped[float] = mapped_column(default=0.0)
    buy_box_percentage: Mapped[float] = mapped_column(default=0.0)
    units_ordered: Mapped[int] = mapped_column(default=0)
    unit_session_percentage: Mapped[float] = mapped_column(default=0.0)
    ordered_product_sales: Mapped[float] = mapped_column(default=0.0)
    total_order_items: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Add store relationship
    store: Mapped["Store"] = relationship("Store", back_populates="business_reports")

    def __repr__(self) -> str:
        return f"<BusinessReport {self.asin} @ {self.date}>"

__all__ = ['BusinessReport']
