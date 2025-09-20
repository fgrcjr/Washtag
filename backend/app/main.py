from fastapi import FastAPI
from app.database.database import engine, Base
from app.routers import client, category, order, price
from app.models import price as price_model  # Import to ensure table creation

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title="Laundry POS System",
    description="A Point of Sale system for laundry business with client management",
    version="1.0.0"
)

# Include routers
app.include_router(client.router, prefix="/api/v1")
app.include_router(category.router, prefix="/api/v1")
app.include_router(order.router, prefix="/api/v1")
app.include_router(price.router, prefix="/api/v1/prices", tags=["prices"])

@app.get("/")
def read_root():
    """Root endpoint with basic information"""
    return {
        "message": "Welcome to Laundry POS System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "laundry-pos"}