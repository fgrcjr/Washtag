from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get a single order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_order_with_details(db: Session, order_id: int) -> Optional[Order]:
    """Get a single order by ID with client and category details"""
    return db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.category)
    ).filter(Order.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get multiple orders with pagination"""
    return db.query(Order).offset(skip).limit(limit).all()


def get_orders_with_details(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get multiple orders with client and category details"""
    return db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.category)
    ).offset(skip).limit(limit).all()


def get_orders_by_client(db: Session, client_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders for a specific client"""
    return db.query(Order).filter(Order.client_id == client_id).offset(skip).limit(limit).all()


def get_orders_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders for a specific category"""
    return db.query(Order).filter(Order.category_id == category_id).offset(skip).limit(limit).all()


def get_orders_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders by status"""
    return db.query(Order).filter(Order.status == status).offset(skip).limit(limit).all()


def create_order(db: Session, order: OrderCreate) -> Order:
    """Create a new order"""
    db_order = Order(
        client_id=order.client_id,
        category_id=order.category_id,
        status=order.status,
        total_amount=order.total_amount,
        notes=order.notes
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order: OrderUpdate) -> Optional[Order]:
    """Update an existing order"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order:
        update_data = order.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    """Delete an order"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False