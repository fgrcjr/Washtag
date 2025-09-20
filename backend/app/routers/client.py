from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.crud import client as crud_client

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db)
):
    """Create a new client"""
    return crud_client.create_client(db=db, client=client)


@router.get("/", response_model=List[ClientResponse])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all clients with pagination"""
    clients = crud_client.get_clients(db, skip=skip, limit=limit)
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
def read_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get a single client by ID"""
    db_client = crud_client.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Update a client"""
    # Check if client exists
    db_client = crud_client.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    updated_client = crud_client.update_client(db=db, client_id=client_id, client=client)
    return updated_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Delete a client"""
    success = crud_client.delete_client(db=db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return None