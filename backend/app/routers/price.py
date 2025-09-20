from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database.database import get_db
from app.crud import price as price_crud
from app.schemas.price import PriceCreate, PriceUpdate, PriceResponse, PriceWithCategory
from app.crud import category as category_crud
from app.models.price import Price

router = APIRouter()


@router.post("/", response_model=PriceResponse)
def create_price(price: PriceCreate, db: Session = Depends(get_db)):
    """Create a new price entry"""
    # Verify category exists
    category = category_crud.get_category(db, price.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check for overlapping weight ranges in the same category and type
    # For Custom type, we only check weight_max, for others we check the range
    if price.type.lower() == 'custom':
        # For Custom type, check if there's already a Custom price for this category
        existing_custom = db.query(Price).filter(
            and_(
                Price.category_id == price.category_id,
                Price.type.ilike('%custom%')
            )
        ).first()
        if existing_custom:
            raise HTTPException(
                status_code=400, 
                detail=f"Custom price already exists for this category"
            )
    else:
        # For non-Custom types, check weight range overlap
        existing_price = price_crud.get_price_by_type_and_weight(
            db, price.category_id, price.type, (price.weight_min + price.weight_max) / 2
        )
        if existing_price:
            raise HTTPException(
                status_code=400, 
                detail=f"Price already exists for type '{price.type}' in this weight range for the selected category"
            )
    
    return price_crud.create_price(db=db, price=price)


@router.get("/", response_model=List[PriceResponse])
def get_prices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    type_filter: Optional[str] = Query(None, description="Filter by type name"),
    db: Session = Depends(get_db)
):
    """Get all prices with optional filtering"""
    return price_crud.get_prices(
        db=db, 
        skip=skip, 
        limit=limit, 
        category_id=category_id,
        type_filter=type_filter
    )


@router.get("/category/{category_id}", response_model=List[PriceResponse])
def get_prices_by_category(category_id: int, db: Session = Depends(get_db)):
    """Get all prices for a specific category"""
    # Verify category exists
    category = category_crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return price_crud.get_prices_by_category(db=db, category_id=category_id)


@router.get("/calculate", response_model=PriceResponse)
def calculate_price(
    category_id: int = Query(..., description="Category ID"),
    weight: float = Query(..., gt=0, description="Weight in kg"),
    type_name: Optional[str] = Query(None, description="Type of clothing or service"),
    db: Session = Depends(get_db)
):
    """Calculate price based on weight and category"""
    # Verify category exists
    category = category_crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    price = price_crud.get_price_by_weight_range(
        db=db, 
        category_id=category_id, 
        weight=weight, 
        type_filter=type_name
    )
    
    if not price:
        raise HTTPException(
            status_code=404, 
            detail=f"No price found for weight {weight}kg in category '{category.name}'"
        )
    
    return price


@router.get("/{price_id}", response_model=PriceWithCategory)
def get_price(price_id: int, db: Session = Depends(get_db)):
    """Get a specific price by ID"""
    price = price_crud.get_price(db=db, price_id=price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    
    # Get category information
    category = category_crud.get_category(db, price.category_id)
    price_dict = price.__dict__.copy()
    price_dict['category'] = {
        'id': category.id,
        'name': category.name,
        'created_at': category.created_at,
        'updated_at': category.updated_at
    }
    
    return PriceWithCategory(**price_dict)


@router.put("/{price_id}", response_model=PriceResponse)
def update_price(price_id: int, price: PriceUpdate, db: Session = Depends(get_db)):
    """Update a price entry"""
    # Verify price exists
    existing_price = price_crud.get_price(db, price_id)
    if not existing_price:
        raise HTTPException(status_code=404, detail="Price not found")
    
    # If category_id is being updated, verify new category exists
    if price.category_id is not None:
        category = category_crud.get_category(db, price.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    # Check for overlapping weight ranges if type or weight ranges are being updated
    if price.type is not None or price.weight_min is not None or price.weight_max is not None:
        type_name = price.type if price.type is not None else existing_price.type
        weight_min = price.weight_min if price.weight_min is not None else existing_price.weight_min
        weight_max = price.weight_max if price.weight_max is not None else existing_price.weight_max
        category_id = price.category_id if price.category_id is not None else existing_price.category_id
        
        if type_name.lower() == 'custom':
            # For Custom type, check if there's already a Custom price for this category
            existing_custom = db.query(Price).filter(
                and_(
                    Price.category_id == category_id,
                    Price.type.ilike('%custom%'),
                    Price.id != price_id
                )
            ).first()
            if existing_custom:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Custom price already exists for this category"
                )
        else:
            # For non-Custom types, check weight range overlap
            overlapping_price = price_crud.get_price_by_type_and_weight(
                db, category_id, type_name, (weight_min + weight_max) / 2
            )
            if overlapping_price and overlapping_price.id != price_id:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Price already exists for type '{type_name}' in this weight range for the selected category"
                )
    
    updated_price = price_crud.update_price(db=db, price_id=price_id, price=price)
    return updated_price


@router.delete("/{price_id}")
def delete_price(price_id: int, db: Session = Depends(get_db)):
    """Delete a price entry"""
    success = price_crud.delete_price(db=db, price_id=price_id)
    if not success:
        raise HTTPException(status_code=404, detail="Price not found")
    
    return {"message": "Price deleted successfully"}
