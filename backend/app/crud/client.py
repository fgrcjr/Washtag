from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


def get_client(db: Session, client_id: int) -> Optional[Client]:
    """Get a single client by ID"""
    return db.query(Client).filter(Client.id == client_id).first()


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """Get multiple clients with pagination"""
    return db.query(Client).offset(skip).limit(limit).all()


def create_client(db: Session, client: ClientCreate) -> Client:
    """Create a new client"""
    db_client = Client(
        name=client.name,
        contact_number=client.contact_number,
        address=client.address
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: int, client: ClientUpdate) -> Optional[Client]:
    """Update an existing client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client:
        update_data = client.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_client, field, value)
        db.commit()
        db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> bool:
    """Delete a client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False