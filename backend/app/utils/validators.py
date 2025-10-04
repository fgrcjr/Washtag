"""
Common validation utilities to eliminate repetitive validation patterns
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Any


def validate_entity_exists(
    entity: Optional[Any],
    entity_name: str,
    entity_id: Optional[int] = None
) -> None:
    """
    Validate that an entity exists, raise 404 if not
    
    Args:
        entity: Entity object to check (None if not found)
        entity_name: Name of the entity type (e.g., "Client", "Category")
        entity_id: Optional ID for better error messages
        
    Raises:
        HTTPException: 404 error if entity is None
    """
    if entity is None:
        detail = f"{entity_name} not found"
        if entity_id is not None:
            detail = f"{entity_name} with ID {entity_id} not found"
        raise HTTPException(status_code=404, detail=detail)


def validate_unique_constraint(
    exists: bool,
    field_name: str,
    field_value: Any,
    entity_name: str
) -> None:
    """
    Validate that a unique constraint is not violated
    
    Args:
        exists: True if entity with this value already exists
        field_name: Name of the field (e.g., "name", "contact_number")
        field_value: Value that should be unique
        entity_name: Name of the entity type (e.g., "Client", "Category")
        
    Raises:
        HTTPException: 400 error if constraint would be violated
    """
    if exists:
        raise HTTPException(
            status_code=400,
            detail=f"{entity_name} with {field_name} '{field_value}' already exists"
        )


def validate_operation_success(
    success: bool,
    operation: str,
    entity_name: str,
    entity_id: Optional[int] = None
) -> None:
    """
    Validate that an operation was successful
    
    Args:
        success: Whether the operation succeeded
        operation: Name of the operation (e.g., "delete", "update")
        entity_name: Name of the entity type
        entity_id: Optional ID for better error messages
        
    Raises:
        HTTPException: 404 error if operation failed
    """
    if not success:
        detail = f"Failed to {operation} {entity_name}"
        if entity_id is not None:
            detail = f"{entity_name} with ID {entity_id} not found"
        raise HTTPException(status_code=404, detail=detail)

