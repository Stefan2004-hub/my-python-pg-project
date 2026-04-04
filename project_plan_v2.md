# Project Plan v2: Python FastAPI with Spring-like Architecture and Pandas

## Overview
This plan outlines the implementation of a Python application with a Spring-like architecture using FastAPI, SQLAlchemy, Pydantic, and Pandas. The application will interface with an existing PostgreSQL database containing e-commerce data (categories, products, customers, orders, order_items).

---

## 1. Architecture (Spring Boot Equivalent)

| Java Spring Component | Python (FastAPI) Equivalent |
| :--- | :--- |
| **Entity** | **SQLAlchemy Models** (Declarative Base) |
| **DTO** | **Pydantic Models** (Data validation & serialization) |
| **Repository** | **SQLAlchemy CRUD** (or a dedicated Repository class) |
| **Service** | **Business Logic Layer** (Functions or Classes) |
| **Controller** | **FastAPI APIRouter** |
| **Exception Handler** | **FastAPI Exception Handlers** (`@app.exception_handler`) |
| **TestContainers** | **testcontainers-python** |

---

## 2. Project Structure

```text
my_app/
├── app/
│   ├── api/                # Controllers (Routes)
│   │   └── routes/
│   │       ├── products.py
│   │       ├── categories.py
│   │       ├── orders.py
│   │       └── reports.py
│   ├── core/               # Config, Security, Database connection
│   │   ├── config.py       # Settings management
│   │   ├── database.py     # DB session & engine
│   │   └── exceptions.py   # Custom exceptions
│   ├── models/             # SQLAlchemy Entities
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── order_item.py
│   ├── schemas/            # Pydantic DTOs
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── common.py       # Shared schemas
│   ├── repositories/       # Database access logic
│   │   ├── category_repository.py
│   │   ├── product_repository.py
│   │   ├── customer_repository.py
│   │   └── order_repository.py
│   ├── services/           # Business logic
│   │   ├── category_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── report_service.py  # Pandas reports
│   └── main.py             # App entry point
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Testcontainers tests
├── docker-compose.yml      # Local Postgres & App
├── init.sql                # Database initialization script
├── requirements.txt
└── README.md
```

---

## 3. Implementation Steps (20 minutes each)

### Phase 1: Project Setup (60 minutes)

**Step 1.1: Environment Setup (20 minutes)**
- Create project directory structure
- Set up virtual environment
- Install core dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `psycopg2-binary`
- Create `requirements.txt` with all dependencies
- Create basic `docker-compose.yml` for PostgreSQL

**Step 1.2: Database Connection (20 minutes)**
- Set up `app/core/config.py` with Pydantic Settings
- Configure environment variables (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
- Create `app/core/database.py` with SQLAlchemy engine and session management
- Test database connection
- Create the `init.sql` loader logic

**Step 1.3: Core Infrastructure (20 minutes)**
- Create custom exceptions in `app/core/exceptions.py`
- Set up global exception handlers in `app/main.py`
- Configure CORS middleware
- Create health check endpoint

---

### Phase 2: Data Models (60 minutes)

**Step 2.1: SQLAlchemy Models - Part 1 (20 minutes)**
- Create base model in `app/models/__init__.py`
- Create `Category` model
- Create `Product` model
- Create relationship between Product and Category

**Step 2.2: SQLAlchemy Models - Part 2 (20 minutes)**
- Create `Customer` model
- Create `Order` model
- Create `OrderItem` model
- Define all relationships (Order -> Customer, Order -> OrderItems -> Product)

**Step 2.3: Pydantic Schemas (20 minutes)**
- Create base schemas in `app/schemas/common.py`
- Create CRUD schemas for Category (Create, Update, Response)
- Create CRUD schemas for Product
- Create CRUD schemas for Customer
- Create CRUD schemas for Order with nested items

---

### Phase 3: Repositories (60 minutes)

**Step 3.1: Category & Product Repositories (20 minutes)**
- Create `app/repositories/category_repository.py` with CRUD operations
- Create `app/repositories/product_repository.py` with CRUD operations
- Add filtering and pagination support
- Add search by name/description

**Step 3.2: Customer & Order Repositories (20 minutes)**
- Create `app/repositories/customer_repository.py` with CRUD operations
- Create `app/repositories/order_repository.py` with CRUD operations
- Implement order creation with items
- Add order status filtering

**Step 3.3: Repository Testing (20 minutes)**
- Write unit tests for repositories
- Test CRUD operations with in-memory SQLite
- Verify relationship loading

---

### Phase 4: Services (80 minutes)

**Step 4.1: Category & Product Services (20 minutes)**
- Create `app/services/category_service.py`
- Create `app/services/product_service.py`
- Implement business logic (validation, calculations)
- Add service layer validation

**Step 4.2: Order Service (20 minutes)**
- Create `app/services/order_service.py`
- Implement order creation workflow
- Add inventory checking logic
- Calculate order totals

**Step 4.3: Pandas Integration - Basic (20 minutes)**
- Install pandas: `pip install pandas`
- Create `app/services/report_service.py`
- **Pandas Basics 1**: Load data from SQLAlchemy query to DataFrame
- **Pandas Basics 2**: Use `df.head()`, `df.describe()`, `df.info()` for data exploration

**Step 4.4: Pandas Integration - Reports (20 minutes)**
- **Pandas Basics 3**: Group data with `df.groupby()` (e.g., sales by category)
- **Pandas Basics 4**: Use `df.sort_values()` for ranking
- **Pandas Basics 5**: Calculate aggregations (sum, mean, count)
- Create API endpoint to return pandas results as JSON

---

### Phase 5: API Controllers (60 minutes)

**Step 5.1: Category & Product Routes (20 minutes)**
- Create `app/api/routes/categories.py`
- Create `app/api/routes/products.py`
- Implement GET, POST, PUT, DELETE endpoints
- Add query parameters for filtering

**Step 5.2: Order Routes (20 minutes)**
- Create `app/api/routes/orders.py`
- Implement order creation endpoint
- Implement order retrieval by ID
- List orders with filters

**Step 5.3: Report Routes (20 minutes)**
- Create `app/api/routes/reports.py`
- Create endpoints for each report type
- Return pandas DataFrame results as JSON
- Add pagination for large result sets

---

### Phase 6: Testing & Documentation (60 minutes)

**Step 6.1: Integration Testing with Testcontainers (20 minutes)**
- Install testcontainers: `pip install testcontainers`
- Create `tests/conftest.py` with PostgreSQL fixture
- Write integration tests for API endpoints
- Verify database operations

**Step 6.2: API Documentation (20 minutes)**
- Review auto-generated OpenAPI docs
- Add descriptive endpoint docstrings
- Add examples to Pydantic schemas
- Test API documentation

**Step 6.3: Final Testing & Cleanup (20 minutes)**
- Run all tests
- Fix any issues
- Verify pandas reports work correctly
- Clean up code and add comments where needed

---

## 4. Pandas Integration Details

### 4.1 Basic Pandas Operations for This Database

```python
# app/services/report_service.py
import pandas as pd
from sqlalchemy.orm import Session

# Load data from database
def load_order_data(db: Session):
    query = db.query(OrderItem).statement
    df = pd.read_sql(query, db.bind)
    return df

# Basic DataFrame operations
def explore_data(df):
    # Get first 5 rows
    df.head()
    
    # Get statistics
    df.describe()
    
    # Get column info
    df.info()
    
    # Select columns
    df[['product_id', 'quantity', 'line_total']]
```

### 4.2 Grouping and Aggregation

```python
# Sales by product
def sales_by_product(df):
    return df.groupby('product_id')['line_total'].sum().reset_index()

# Sales by category
def sales_by_category(db: Session):
    query = db.query(
        Product.category_id,
        func.sum(OrderItem.line_total).label('total')
    ).join(OrderItem).group_by(Product.category_id).statement
    df = pd.read_sql(query, db.bind)
    return df.groupby('category_id')['total'].sum().reset_index()

# Order statistics
def order_statistics(orders_df):
    return {
        'total_orders': len(orders_df),
        'total_revenue': orders_df['total_amount'].sum(),
        'avg_order_value': orders_df['total_amount'].mean(),
        'max_order': orders_df['total_amount'].max(),
        'min_order': orders_df['total_amount'].min()
    }
```

### 4.3 Common Reports to Implement

1. **Sales by Product**: Total revenue per product
2. **Sales by Category**: Total revenue per category
3. **Customer Order History**: Orders per customer
4. **Top Products**: Best selling products by quantity
5. **Daily Sales**: Sales aggregated by day
6. **Customer Segmentation**: RFM (Recency, Frequency, Monetary) analysis

---

## 5. Database Schema Reference

Based on your `init.sql`, here are the tables:

### Tables
- **categories**: id, name, description
- **products**: id, name, description, price, category_id
- **customers**: id, first_name, last_name, email, phone, address, city, state, zip_code
- **orders**: id, customer_id, order_date, total_amount, status
- **order_items**: id, order_id, product_id, quantity, unit_price, line_total

### Sample Queries for Pandas

```python
# Query 1: Get all products with category
query = db.query(
    Product.id,
    Product.name,
    Product.price,
    Category.name.label('category')
).join(Category).statement

# Query 2: Get order items with product details
query = db.query(
    OrderItem,
    Product.name.label('product_name'),
    Order.id.label('order_id'),
    Order.order_date
).join(Product).join(Order).statement
```

---

## 6. Summary of Best Practices

1. **Dependency Injection**: Use FastAPI's `Depends()` to inject Database Session or Services into Controllers
2. **Async vs Sync**: For Pandas operations, use standard `def` routes (sync) or run with `run_in_threadpool` since Pandas is CPU-bound
3. **Migrations**: Consider using Alembic for long-term database versioning
4. **Error Handling**: Create global exception handler in `main.py` for custom exceptions
5. **Validation**: Use Pydantic for all input validation
6. **Testing**: Use Testcontainers for integration tests with real PostgreSQL

---

## 7. Next Steps

1. Start with Phase 1 (Project Setup)
2. Complete each step sequentially
3. Test each component before moving to the next phase
4. Run pandas queries to verify data loads correctly
5. Deploy using Docker Compose

---

*Generated: April 2026*
