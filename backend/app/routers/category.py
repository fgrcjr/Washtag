from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud import category as crud_category
from app.utils.validators import validate_entity_exists, validate_operation_success, validate_unique_constraint

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
    db_category = crud_category.get_category_by_name(db, name=category.name)
    validate_unique_constraint(db_category is not None, "name", category.name, "Category")
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
    validate_entity_exists(db_category, "Category", category_id)
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category"""
    db_category = crud_category.get_category(db, category_id=category_id)
    validate_entity_exists(db_category, "Category", category_id)
    
    # Check if name is being updated and if it already exists
    if category.name and category.name != db_category.name:
        existing_category = crud_category.get_category_by_name(db, name=category.name)
        validate_unique_constraint(existing_category is not None, "name", category.name, "Category")
    
    updated_category = crud_category.update_category(db=db, category_id=category_id, category=category)
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a category"""
    success = crud_category.delete_category(db=db, category_id=category_id)
    validate_operation_success(success, "delete", "Category", category_id)
    return None