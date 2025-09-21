from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.order import Order
from app.models.client import Client
from app.models.category import Category
from app.models.price import Price
from app.schemas.order import OrderCreate, OrderUpdate, IntegratedOrderCreate, IntegratedOrderResponse
from app.schemas.client import ClientCreate
from app.crud import client as client_crud
from app.crud import category as category_crud
from app.crud import price as price_crud


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


# Integrated Order Functions for New Client Workflow
def find_or_create_client(db: Session, client_name: str, client_contact: str, client_address: str) -> Client:
    """Find existing client by contact number or create new one"""
    
    # First try to find by contact number
    existing_client = db.query(Client).filter(Client.contact_number == client_contact).first()
    if existing_client:
        return existing_client
    
    # If not found, create new client
    client_data = ClientCreate(
        name=client_name,
        contact_number=client_contact,
        address=client_address
    )
    return client_crud.create_client(db=db, client=client_data)


def get_price_for_order(db: Session, category_id: int, type_name: str, weight: float, custom_amount: Optional[float] = None) -> Tuple[Optional[Price], float]:
    """
    Get price for order based on type and weight
    Returns (price_object, final_amount)
    """
    
    # If custom type, use custom amount
    if type_name.lower() == 'custom':
        if custom_amount is None:
            raise ValueError("custom_amount is required for custom type")
        return None, custom_amount
    
    # For predefined types, find matching price
    price = price_crud.get_price_by_type_and_weight(
        db=db,
        category_id=category_id,
        type_name=type_name,
        weight=weight
    )
    
    if not price:
        # Try to find any price in the category that matches the weight range
        price = price_crud.get_price_by_weight_range(
            db=db,
            category_id=category_id,
            weight=weight,
            type_filter=type_name
        )
    
    if not price:
        raise ValueError(f"No price found for type '{type_name}' with weight {weight}kg in category {category_id}")
    
    return price, price.amount


def create_integrated_order(db: Session, order_data: IntegratedOrderCreate) -> IntegratedOrderResponse:
    """Create an integrated order with automatic client handling and price calculation"""
    
    # Validate category exists
    category = category_crud.get_category(db, category_id=order_data.category_id)
    if not category:
        raise ValueError(f"Category with ID {order_data.category_id} not found")
    
    # Find or create client
    client = find_or_create_client(
        db=db,
        client_name=order_data.client_name,
        client_contact=order_data.client_contact,
        client_address=order_data.client_address
    )
    
    # Get price for the order
    price_obj, total_amount = get_price_for_order(
        db=db,
        category_id=order_data.category_id,
        type_name=order_data.type_name,
        weight=order_data.weight,
        custom_amount=order_data.custom_amount
    )
    
    # Create order
    order_create = OrderCreate(
        client_id=client.id,
        category_id=order_data.category_id,
        status=order_data.status,
        total_amount=total_amount,
        notes=order_data.notes
    )
    
    order = create_order(db=db, order=order_create)
    
    # Return comprehensive response
    return IntegratedOrderResponse(
        order_id=order.id,
        status=order.status,
        total_amount=order.total_amount,
        notes=order.notes,
        created_at=order.created_at.isoformat(),
        client_id=client.id,
        client_name=client.name,
        client_contact=client.contact_number,
        client_address=client.address,
        category_id=category.id,
        category_name=category.name,
        type_name=order_data.type_name,
        weight=order_data.weight,
        price_id=price_obj.id if price_obj else None
    )