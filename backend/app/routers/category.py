from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud import category as crud_category

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    # Check if category with this name already exists
    db_category = crud_category.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=400,
            detail="Category name already exists"
        )
    return crud_category.create_category(db=db, category=category)


@router.get("/", response_model=List[CategoryResponse])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all categories with pagination"""
    categories = crud_category.get_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get a single category by ID"""
    db_category = crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category"""
    # Check if category exists
    db_category = crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if name is being updated and if it already exists
    if category.name and category.name != db_category.name:
        existing_category = crud_category.get_category_by_name(db, name=category.name)
        if existing_category:
            raise HTTPException(
                status_code=400,
                detail="Category name already exists"
            )
    
    updated_category = crud_category.update_category(db=db, category_id=category_id, category=category)
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a category"""
    success = crud_category.delete_category(db=db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return None