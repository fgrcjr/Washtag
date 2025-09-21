from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderResponseWithDetails, OrderStatus, IntegratedOrderCreate, IntegratedOrderResponse
from app.crud import order as crud_order
from app.crud import client as crud_client
from app.crud import category as crud_category

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """Create a new order"""
    # Validate client exists
    client = crud_client.get_client(db, client_id=order.client_id)
    if not client:
        raise HTTPException(
            status_code=400,
            detail="Client not found"
        )
    
    # Validate category exists
    category = crud_category.get_category(db, category_id=order.category_id)
    if not category:
        raise HTTPException(
            status_code=400,
            detail="Category not found"
        )
    
    return crud_order.create_order(db=db, order=order)


@router.get("/", response_model=List[OrderResponse])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get all orders with optional filtering"""
    if client_id:
        orders = crud_order.get_orders_by_client(db, client_id=client_id, skip=skip, limit=limit)
    elif category_id:
        orders = crud_order.get_orders_by_category(db, category_id=category_id, skip=skip, limit=limit)
    elif status:
        orders = crud_order.get_orders_by_status(db, status=status.value, skip=skip, limit=limit)
    else:
        orders = crud_order.get_orders(db, skip=skip, limit=limit)
    return orders


@router.get("/details", response_model=List[OrderResponseWithDetails])
def read_orders_with_details(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all orders with client and category details"""
    orders = crud_order.get_orders_with_details(db, skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def read_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get a single order by ID"""
    db_order = crud_order.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.get("/{order_id}/details", response_model=OrderResponseWithDetails)
def read_order_with_details(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get a single order by ID with client and category details"""
    db_order = crud_order.get_order_with_details(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Update an order"""
    # Check if order exists
    db_order = crud_order.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate client exists if client_id is being updated
    if order.client_id is not None:
        client = crud_client.get_client(db, client_id=order.client_id)
        if not client:
            raise HTTPException(
                status_code=400,
                detail="Client not found"
            )
    
    # Validate category exists if category_id is being updated
    if order.category_id is not None:
        category = crud_category.get_category(db, category_id=order.category_id)
        if not category:
            raise HTTPException(
                status_code=400,
                detail="Category not found"
            )
    
    updated_order = crud_order.update_order(db=db, order_id=order_id, order=order)
    return updated_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Delete an order"""
    success = crud_order.delete_order(db=db, order_id=order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return None


# Integrated Order Endpoint for New Client Workflow
@router.post("/integrated", response_model=IntegratedOrderResponse, status_code=status.HTTP_201_CREATED)
def create_integrated_order(
    order: IntegratedOrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new order with integrated client handling and price calculation.
    
    This endpoint handles the complete workflow:
    1. Checks if client exists (by contact number), creates if not found
    2. Validates category exists
    3. Calculates price based on type and weight:
       - For predefined types: finds matching price from database
       - For 'custom' type: uses provided custom_amount
    4. Creates order with all details
    5. Returns comprehensive order information including client, category, and pricing details
    
    **Pricing Logic:**
    - **Predefined Types**: System automatically finds the appropriate price based on type and weight
    - **Custom Type**: Uses the provided custom_amount (required when type_name is 'custom')
    
    **Client Handling:**
    - If client with same contact number exists, uses existing client
    - If not found, creates new client with provided information
    """
    try:
        return crud_order.create_integrated_order(db=db, order_data=order)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )