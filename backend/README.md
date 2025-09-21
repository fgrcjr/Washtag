# Laundry POS System

A FastAPI-based Point of Sale system for laundry businesses with client management functionality.

## Features

- **Client Management**: Full CRUD operations for client data
- **Category Management**: Organize services and products by categories
- **Order Management**: Track and manage customer orders
- **Price Management**: Dynamic pricing based on weight ranges and clothing types
- **RESTful API**: Clean and well-documented API endpoints
- **Database Integration**: SQLAlchemy with SQLite database
- **Data Validation**: Pydantic models for request/response validation
- **Interactive Documentation**: Swagger UI and ReDoc
- **Modular Architecture**: Well-organized code structure with separate modules for models, schemas, CRUD operations, and API routes

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── models/              # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── client.py        # Client model
│   │   ├── category.py      # Category model
│   │   ├── order.py         # Order model
│   │   └── price.py         # Price model
│   ├── schemas/             # Pydantic models for request/response validation
│   │   ├── __init__.py
│   │   ├── client.py        # Client schemas
│   │   ├── category.py      # Category schemas
│   │   ├── order.py         # Order schemas
│   │   └── price.py         # Price schemas
│   ├── crud/                # CRUD operations
│   │   ├── __init__.py
│   │   ├── client.py        # Client CRUD operations
│   │   ├── category.py      # Category CRUD operations
│   │   ├── order.py         # Order CRUD operations
│   │   └── price.py         # Price CRUD operations
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── client.py        # Client API routes
│   │   ├── category.py      # Category API routes
│   │   ├── order.py         # Order API routes
│   │   └── price.py         # Price API routes
│   └── database/            # Database configuration
│       ├── __init__.py
│       └── database.py      # Database connection and session management
├── bin/                     # Virtual environment binaries
├── lib/                     # Virtual environment libraries
├── include/                 # Virtual environment includes
├── activate                 # Virtual environment activation script
├── pyvenv.cfg              # Virtual environment configuration
├── requirements.txt         # Python dependencies
├── laundry_pos.db          # SQLite database file
└── README.md               # This file
```

## Setup Instructions

### 1. Navigate to the project directory
```bash
cd backend
```

### 2. Activate the virtual environment
```bash
source activate
```

### 3. Install dependencies (if needed)
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
uvicorn app.main:app --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Client Management
- `POST /api/v1/clients/` - Create a new client
- `GET /api/v1/clients/` - Get all clients (with pagination)
- `GET /api/v1/clients/{client_id}` - Get a specific client
- `PUT /api/v1/clients/{client_id}` - Update a client
- `DELETE /api/v1/clients/{client_id}` - Delete a client

### Category Management
- `POST /api/v1/categories/` - Create a new category
- `GET /api/v1/categories/` - Get all categories (with pagination)
- `GET /api/v1/categories/{category_id}` - Get a specific category
- `PUT /api/v1/categories/{category_id}` - Update a category
- `DELETE /api/v1/categories/{category_id}` - Delete a category

### Order Management
- `POST /api/v1/orders/` - Create a new order
- `GET /api/v1/orders/` - Get all orders (with pagination)
- `GET /api/v1/orders/{order_id}` - Get a specific order
- `PUT /api/v1/orders/{order_id}` - Update an order
- `DELETE /api/v1/orders/{order_id}` - Delete an order

### Price Management
- `POST /api/v1/prices/` - Create a new price entry
- `GET /api/v1/prices/` - Get all prices (with filtering by category and type)
- `GET /api/v1/prices/category/{category_id}` - Get all prices for a specific category
- `GET /api/v1/prices/calculate` - Calculate price based on weight and category
- `GET /api/v1/prices/{price_id}` - Get a specific price with category details
- `PUT /api/v1/prices/{price_id}` - Update a price entry
- `DELETE /api/v1/prices/{price_id}` - Delete a price entry

### Health Checks
- `GET /` - Root endpoint with basic information
- `GET /health` - Health check endpoint

## Client Data Structure

```json
{
  "name": "John Doe",
  "contact_number": "+1234567890",
  "address": "123 Main St, City, State 12345"
}
```

## Example Usage

### Creating a client
```bash
curl -X POST "http://localhost:8000/api/v1/clients/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Jane Smith",
       "contact_number": "+1234567890",
       "address": "456 Oak Ave, City, State 67890"
     }'
```

### Getting all clients
```bash
curl -X GET "http://localhost:8000/api/v1/clients/"
```

### Getting a specific client
```bash
curl -X GET "http://localhost:8000/api/v1/clients/1"
```

### Updating a client
```bash
curl -X PUT "http://localhost:8000/api/v1/clients/1" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Jane Doe",
       "contact_number": "+0987654321"
     }'
```

### Deleting a client
```bash
curl -X DELETE "http://localhost:8000/api/v1/clients/1"
```

### Creating a price entry
```bash
curl -X POST "http://localhost:8000/api/v1/prices/" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "Clothes",
       "weight_min": 0.1,
       "weight_max": 6.0,
       "amount": 175.00,
       "category_id": 1
     }'
```

### Calculating price based on weight
```bash
curl -X GET "http://localhost:8000/api/v1/prices/calculate?category_id=1&weight=3.5&type_name=Clothes"
```

### Getting all prices for a category
```bash
curl -X GET "http://localhost:8000/api/v1/prices/category/1"
```

### Creating an integrated order (New Client Workflow)
```bash
# For predefined type (automatic price calculation)
curl -X POST "http://localhost:8000/api/v1/orders/integrated" \
     -H "Content-Type: application/json" \
     -d '{
       "client_name": "John Doe",
       "client_contact": "12345678901",
       "client_address": "123 Main St, City, State 12345",
       "category_id": 1,
       "type_name": "Clothes",
       "weight": 3.5,
       "notes": "Regular wash"
     }'

# For custom type (manual price)
curl -X POST "http://localhost:8000/api/v1/orders/integrated" \
     -H "Content-Type: application/json" \
     -d '{
       "client_name": "Jane Smith",
       "client_contact": "09876543210",
       "client_address": "456 Oak Ave, City, State 67890",
       "category_id": 1,
       "type_name": "Custom",
       "weight": 5.0,
       "custom_amount": 250.00,
       "notes": "Special handling required"
     }'
```

## Integrated Order Workflow

The system now supports a complete integrated workflow for new clients through the `/api/v1/orders/integrated` endpoint. This handles the exact scenario you described:

### Workflow Steps:
1. **New Client Detection**: System checks if client exists by contact number
2. **Client Creation**: If not found, automatically creates new client
3. **Category Selection**: Validates the selected category exists
4. **Price Calculation**: 
   - **Predefined Types**: Automatically finds matching price based on type and weight
   - **Custom Type**: Uses provided custom_amount
5. **Order Creation**: Creates order with all details
6. **Order Display**: Returns comprehensive order information

### Pricing Logic:
- **Predefined Types** (e.g., "Clothes", "Bedding"): System automatically selects appropriate price from database based on weight ranges
- **Custom Type**: Requires `custom_amount` field and uses that value directly

### Response Format:
The integrated order endpoint returns complete order information including:
- Order details (ID, status, amount, creation date)
- Client information (ID, name, contact, address)
- Category information (ID, name)
- Pricing details (type, weight, price ID for predefined types)

## Development

The application uses SQLite as the default database. The database file (`laundry_pos.db`) will be created automatically when you first run the application.

### Database Models

- **Client**: Stores client information including name, contact_number, address, and timestamps
- **Category**: Organizes services and products into categories with name and description
- **Order**: Tracks customer orders with client relationships, order details, and status information
- **Price**: Manages pricing based on clothing type, weight ranges (min-max), and amounts per category

### Key Features

- **Modular Design**: Clean separation of concerns with dedicated modules for models, schemas, CRUD operations, and API routes
- **Comprehensive CRUD**: Full Create, Read, Update, Delete operations for all entities
- **Pagination**: All listing endpoints support pagination with `skip` and `limit` parameters
- **Data Validation**: All input data is validated using Pydantic models
- **Error Handling**: Proper HTTP status codes and error messages
- **Timestamps**: Automatic creation and update timestamps for all entities
- **Database Relationships**: Proper foreign key relationships between orders, clients, and categories

## Next Steps

This is a comprehensive laundry POS system with client, category, and order management. You can extend it by adding:

- Pricing and billing calculations
- User authentication and authorization
- Payment processing integration
- Inventory management
- Reporting and analytics dashboard
- Email/SMS notifications
- Receipt generation
- Multi-location support