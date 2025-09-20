from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.price import Price
from app.schemas.price import PriceCreate, PriceUpdate


def create_price(db: Session, price: PriceCreate) -> Price:
    """Create a new price entry"""
    db_price = Price(
        type=price.type,
        weight_min=price.weight_min,
        weight_max=price.weight_max,
        amount=price.amount,
        category_id=price.category_id
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price


def get_price(db: Session, price_id: int) -> Optional[Price]:
    """Get a price by ID"""
    return db.query(Price).filter(Price.id == price_id).first()


def get_prices(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None,
    type_filter: Optional[str] = None
) -> List[Price]:
    """Get all prices with optional filtering"""
    query = db.query(Price)
    
    if category_id is not None:
        query = query.filter(Price.category_id == category_id)
    
    if type_filter is not None:
        query = query.filter(Price.type.ilike(f"%{type_filter}%"))
    
    return query.offset(skip).limit(limit).all()


def get_prices_by_category(db: Session, category_id: int) -> List[Price]:
    """Get all prices for a specific category"""
    return db.query(Price).filter(Price.category_id == category_id).all()


def get_price_by_weight_range(
    db: Session, 
    category_id: int, 
    weight: float, 
    type_filter: Optional[str] = None
) -> Optional[Price]:
    """Get price based on weight range and category"""
    query = db.query(Price).filter(
        and_(
            Price.category_id == category_id,
            Price.weight_max >= weight
        )
    )
    
    # For non-Custom types, also check weight_min
    query = query.filter(
        or_(
            Price.type.ilike('%custom%'),
            Price.weight_min <= weight
        )
    )
    
    if type_filter is not None:
        query = query.filter(Price.type.ilike(f"%{type_filter}%"))
    
    return query.first()


def update_price(db: Session, price_id: int, price: PriceUpdate) -> Optional[Price]:
    """Update a price entry"""
    db_price = db.query(Price).filter(Price.id == price_id).first()
    if not db_price:
        return None
    
    update_data = price.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_price, field, value)
    
    db.commit()
    db.refresh(db_price)
    return db_price


def delete_price(db: Session, price_id: int) -> bool:
    """Delete a price entry"""
    db_price = db.query(Price).filter(Price.id == price_id).first()
    if not db_price:
        return False
    
    db.delete(db_price)
    db.commit()
    return True


def get_price_by_type_and_weight(
    db: Session, 
    category_id: int, 
    type_name: str, 
    weight: float
) -> Optional[Price]:
    """Get price for specific type and weight within a category"""
    query = db.query(Price).filter(
        and_(
            Price.category_id == category_id,
            Price.type == type_name,
            Price.weight_max >= weight
        )
    )
    
    # For non-Custom types, also check weight_min
    query = query.filter(
        or_(
            Price.type.ilike('%custom%'),
            Price.weight_min <= weight
        )
    )
    
    return query.first()
