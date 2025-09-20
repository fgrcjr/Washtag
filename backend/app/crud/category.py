from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Get a single category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """Get a category by name"""
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get multiple categories with pagination"""
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: CategoryCreate) -> Category:
    """Create a new category"""
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Optional[Category]:
    """Update an existing category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category:
        update_data = category.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False