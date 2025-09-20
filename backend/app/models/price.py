from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False, index=True, comment="Type of clothing or service")
    weight_min = Column(Float, nullable=True, comment="Minimum weight in kg (null for Custom type)")
    weight_max = Column(Float, nullable=False, comment="Maximum weight in kg")
    amount = Column(Float, nullable=False, comment="Price amount")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="prices")
