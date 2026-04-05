# Code Plan: FastAPI E-Commerce Service with Spring-like Architecture

## Summary
This project will implement a Python web service that follows a Spring-style Controller-Service-Repository structure using FastAPI, SQLAlchemy, Pydantic, PostgreSQL, and Pandas. The application will expose CRUD APIs over an existing e-commerce schema and add reporting endpoints backed by Pandas aggregations.

The work should proceed in dependency order: project setup, database/core infrastructure, models and schemas, repositories, services, API routes, then testing and documentation. Each phase below includes the expected outputs and validation needed before moving forward.

## Architecture and Target Layout

### Layer Mapping
| Spring Concept | Python Equivalent |
| :--- | :--- |
| Entity | SQLAlchemy declarative models |
| DTO | Pydantic schemas |
| Repository | SQLAlchemy data-access layer |
| Service | Business-logic layer |
| Controller | FastAPI `APIRouter` modules |
| Exception Handler | FastAPI exception handlers |
| TestContainers | `testcontainers-python` |

### Intended Repository Layout
```text
my_app/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── products.py
│   │       ├── categories.py
│   │       ├── orders.py
│   │       └── reports.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── order_item.py
│   ├── schemas/
│   │   ├── common.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   └── order.py
│   ├── repositories/
│   │   ├── category_repository.py
│   │   ├── product_repository.py
│   │   ├── customer_repository.py
│   │   └── order_repository.py
│   ├── services/
│   │   ├── category_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── report_service.py
│   └── main.py
├── tests/
│   ├── unit/
│   └── integration/
├── docker-compose.yml
├── init.sql
├── pyproject.toml
└── README.md
```

## Implementation Plan

### Phase 1: Bootstrap the project [done]
- Create the application and test directory structure.
- Create `pyproject.toml` with FastAPI, Uvicorn, SQLAlchemy, Pydantic, psycopg2-binary, pandas, pytest, and testcontainers.
- Add `docker-compose.yml` for local PostgreSQL and app startup.
- Add base README notes for running the app and tests.

Expected outputs:
- Repo has the planned directory skeleton.
- Dependencies are declared in one place.
- Local development can start PostgreSQL consistently.

Validation:
- Dependency install succeeds in a clean virtual environment.
- Docker Compose starts PostgreSQL without manual steps.

### Phase 2: Core configuration and database plumbing [done]
- Implement `app/core/config.py` with environment-based settings for database connection details.
- Implement `app/core/database.py` with SQLAlchemy engine, session factory, and request-scoped DB dependency.
- Wire the existing `init.sql` into local database initialization.
- Add `app/core/exceptions.py` and define base domain errors.
- Create `app/main.py` with FastAPI app setup, CORS configuration, exception handlers, and a health endpoint.

Expected outputs:
- The app can connect to PostgreSQL through a shared session dependency.
- Startup configuration is centralized and reusable.
- A health check confirms the service is running.

Validation:
- App startup succeeds with valid DB environment variables.
- Health endpoint responds successfully.
- DB session dependency can execute a simple query.

### Phase 3: Model the database and API schemas [done]
- Create SQLAlchemy models for `categories`, `products`, `customers`, `orders`, and `order_items`.
- Define relationships:
  product -> category, order -> customer, order -> order_items, order_item -> product.
- Create Pydantic schemas for create, update, and response payloads.
- Add shared schema types in `app/schemas/common.py` for pagination, standard responses, or reusable fields.

Expected outputs:
- ORM models reflect the existing PostgreSQL schema.
- Pydantic schemas cover API input and output for all main resources.
- Response models support ORM-to-schema serialization.

Validation:
- Model metadata matches the intended table and column names.
- Nested order responses serialize correctly.
- Required and optional fields are enforced at the schema layer.

### Phase 4: Build repositories [done]
- Implement CRUD repositories for categories, products, customers, and orders.
- Add product filtering, pagination, and text search over name and description.
- Add order listing with status filtering.
- Implement order creation persistence including nested order items.

Expected outputs:
- Data access logic is isolated from route handlers.
- Repositories expose clear methods for CRUD, filtering, and list use cases.
- Order writes correctly persist both header and line items.

Validation:
- Unit tests cover CRUD operations against SQLite or a lightweight test DB.
- Repository queries load relationships correctly where needed.
- Search, pagination, and status filters behave predictably.

### Phase 5: Add business logic services
- Implement category and product services to handle validation and orchestration beyond raw CRUD.
- Implement order service for order creation workflow, total calculation, and domain validation.
- Add inventory validation only if the database or project requirements expose inventory state; otherwise leave it out of v1.
- Implement `report_service.py` using Pandas to transform SQL query results into API-ready structures.

Expected outputs:
- Route handlers depend on services instead of repositories directly for non-trivial workflows.
- Order totals are derived consistently from item quantity and price data.
- Reporting logic is isolated and reusable.

Validation:
- Service tests verify business rules and failure paths.
- Order total calculation is deterministic.
- Pandas reports return JSON-serializable records, not raw DataFrames.

### Phase 6: Expose API routes
- Add route modules for categories, products, orders, and reports.
- Implement category and product CRUD endpoints.
- Implement order create, get-by-id, and list endpoints.
- Implement report endpoints for at least:
  sales by product, sales by category, customer order history, top products, daily sales.
- Add query parameters for filtering and pagination where planned.

Expected outputs:
- Public API surface is organized by resource.
- FastAPI auto-generates OpenAPI docs from the implemented routes and schemas.
- Report endpoints expose structured analytics results as JSON.

Validation:
- Each route returns the expected status codes and response models.
- Invalid payloads and missing records return controlled errors.
- Filtering and pagination parameters affect results correctly.

### Phase 7: Testing, documentation, and finish criteria
- Add unit tests for repositories and services.
- Add integration tests using `testcontainers-python` with real PostgreSQL.
- Validate end-to-end order creation and report generation flows.
- Expand README with setup, run, test, and API documentation notes.
- Do a final cleanup pass on naming, comments, and module boundaries.

Expected outputs:
- Core business flows are covered by automated tests.
- The app can be started locally and exercised through documented endpoints.
- The implementation is stable enough for iterative feature work.

Validation:
- Test suite passes locally.
- Integration tests verify real PostgreSQL behavior.
- OpenAPI docs load successfully and describe the implemented endpoints.

## Public Interfaces and Expected Behavior

### Core API Areas
- `categories`: create, list, retrieve, update, delete.
- `products`: create, list, retrieve, update, delete, plus filtering and search.
- `orders`: create order with nested items, retrieve by ID, list with status filter.
- `reports`: read-only analytics endpoints that return aggregated JSON results.

### Data Model Scope
- `categories`: `id`, `name`, `description`
- `products`: `id`, `name`, `description`, `price`, `category_id`
- `customers`: `id`, `first_name`, `last_name`, `email`, `phone`, `address`, `city`, `state`, `zip_code`
- `orders`: `id`, `customer_id`, `order_date`, `total_amount`, `status`
- `order_items`: `id`, `order_id`, `product_id`, `quantity`, `unit_price`, `line_total`

### Reporting Scope
- Load SQLAlchemy query results into Pandas DataFrames.
- Use `groupby`, sorting, and basic aggregations to compute report outputs.
- Return report results as dictionaries/lists ready for JSON serialization.

## Test Cases and Acceptance Criteria
- Health check returns success after app startup.
- Category CRUD works end to end.
- Product CRUD works end to end, including filter and search parameters.
- Order creation persists the order and all order items, and calculates totals correctly.
- Order retrieval returns nested item details.
- Invalid input returns 4xx responses with structured error payloads.
- Missing entities return not-found responses through the global exception layer.
- Report endpoints return aggregated results with stable field names.
- Integration tests run against PostgreSQL via Testcontainers, not only SQLite.

## Assumptions and Defaults
- The project starts from an existing `init.sql` schema and should align to that schema rather than redesign it.
- FastAPI routes can be synchronous for v1, especially for Pandas-backed operations.
- Alembic is recommended for future schema evolution but is not required for the first implementation pass.
- Inventory tracking is not part of the confirmed schema, so inventory checks are not mandatory unless added later.
- The first release should prioritize correctness and clean layering over advanced optimizations or async complexity.
