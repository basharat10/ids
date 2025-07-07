# DarziFlow Backend

This is the backend server for the DarziFlow application, designed to streamline tailoring shop operations in Quetta, Pakistan, and similar contexts.

## Project Overview

DarziFlow aims to digitize and manage customer interactions, orders, measurements, karigar (craftsman) assignments, payments, and basic inventory for tailoring businesses. This backend is built using Django and Django REST Framework, providing a robust API for a frontend application (e.g., a Flutter mobile app).

## Features Implemented

The backend currently supports the following core modules:

*   **Authentication:** Secure user registration and JWT-based token authentication (login, refresh, verify, logout with token blacklisting).
*   **Customer Management:** CRUD operations for customers and their multiple measurement sets (with flexible JSON storage for measurements).
*   **Karigar (Craftsman) Management:** CRUD operations for karigars.
*   **Inventory Management (Basic):** CRUD operations for fabrics and accessories.
*   **Order Management:** Comprehensive order processing including:
    *   Creating orders with multiple items.
    *   Linking orders to customers, karigars.
    *   Tracking order status, due dates, pricing (total, advance, due).
    *   Associating order items with specific measurements and fabrics from inventory.
    *   File uploads (voice notes, design images) directly with orders.
*   **Payment Management:** Recording and managing multiple payments against orders.
*   **Advanced Filtering & Searching:** Most list endpoints support searching and filtering for easier data retrieval.

## Technology Stack

*   **Backend Framework:** Django
*   **API Framework:** Django REST Framework (DRF)
*   **Database:** PostgreSQL (recommended, configurable via `DATABASE_URL`, defaults to SQLite for quick setup)
*   **Authentication:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
*   **File Handling:** Direct uploads to media directory, configurable for cloud storage in production.
*   **Dependencies:** `django-cors-headers` (for CORS), `django-filter` (for filtering), `drf-nested-routers` (for nested API routes), `Pillow` (for image processing), `psycopg2-binary` (for PostgreSQL), `dj-database-url` (for DB config).

## Directory Structure Overview

```
darziflow_backend/
├── darziflow_backend/    # Main project configuration (settings.py, urls.py)
├── accounts/             # User authentication, registration
├── core/                 # Core project utilities, base configurations (currently minimal)
├── customers/            # Customer and Measurement management
├── inventory/            # Fabric and Accessory management
├── karigars/             # Karigar (craftsman) management
├── orders/               # Order, OrderItem, and Payment management
├── mediafiles/           # Default location for user-uploaded files (Order voice notes, images)
├── staticfiles/          # Default location for collected static files (for production)
├── manage.py             # Django's command-line utility
├── requirements.txt      # Project dependencies
├── .env.example          # Example environment variables file
└── README.md             # This file
```

## Environment Setup

Follow these steps to set up the local development environment.

### 1. Prerequisites

*   **Python:** Version 3.8+ recommended.
*   **pip:** Python package installer (usually comes with Python).
*   **PostgreSQL:** A running PostgreSQL server. You'll need to create a database and a user for the application. (Alternatively, for a quick test without PostgreSQL, the project will default to SQLite if `DATABASE_URL` is not set in `.env`).
*   **Virtual Environment Tool** (recommended): `venv` (built-in) or `virtualenv`.
*   **Git**

### 2. Clone the Repository

```bash
git clone <your-repository-url> darziflow_backend
cd darziflow_backend
```

### 3. Create and Activate Virtual Environment

```bash
# Using venv (Python 3 built-in)
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Now, edit the `.env` file with your specific settings:

*   `DJANGO_SECRET_KEY`: Generate a new strong secret key. You can use an online generator or Django's `get_random_secret_key()` utility.
*   `DJANGO_DEBUG`: Set to `True` for development, `False` for production.
*   `DJANGO_ALLOWED_HOSTS`: For development, `localhost,127.0.0.1` is usually fine.
*   `DATABASE_URL`: Configure your PostgreSQL connection string.
    *   Format: `postgres://USER:PASSWORD@HOST:PORT/DBNAME`
    *   Example: `postgres://darziuser:darzipass@localhost:5432/darziflow_db`
    *   Ensure the database (`darziflow_db` in the example) and user (`darziuser`) exist in your PostgreSQL server and the user has permissions on the database.
*   `CORS_ALLOWED_ORIGINS`: Update this if your frontend will run on a different port or domain during development (e.g., `http://localhost:8080` for a Vue/React dev server).

### 6. Database Setup

Once your `.env` file is configured (especially `DATABASE_URL`), run database migrations to create the necessary tables:

```bash
python manage.py migrate
```

### 7. Create a Superuser (Optional but Recommended)

This allows access to the Django Admin interface (`/admin/`) for managing data directly.

```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email (optional), and password.

### 8. Run the Development Server

```bash
python manage.py runserver
```
The backend API should now be accessible, typically at `http://127.0.0.1:8000/`.

## API Endpoints Summary

The API is versioned under `/api/v1/`. Here are the main resource groups:

*   **Authentication & Accounts:**
    *   `POST /api/v1/auth/token/`: Obtain JWT access and refresh tokens (Login).
    *   `POST /api/v1/auth/token/refresh/`: Refresh JWT access token.
    *   `POST /api/v1/auth/token/verify/`: Verify JWT access token.
    *   `POST /api/v1/accounts/register/`: Register a new user.
    *   `GET /api/v1/accounts/me/`: Get current authenticated user's details.
    *   `POST /api/v1/accounts/logout/`: Logout (blacklists refresh token).

*   **Customers:**
    *   `GET, POST /api/v1/customers/`
    *   `GET, PUT, PATCH, DELETE /api/v1/customers/{id}/`
    *   **Nested Measurements:**
        *   `GET, POST /api/v1/customers/{customer_pk}/measurements/`
        *   `GET, PUT, PATCH, DELETE /api/v1/customers/{customer_pk}/measurements/{id}/`

*   **Karigars (Craftsmen):**
    *   `GET, POST /api/v1/karigars/`
    *   `GET, PUT, PATCH, DELETE /api/v1/karigars/{id}/`

*   **Inventory:**
    *   **Fabrics:**
        *   `GET, POST /api/v1/inventory/fabrics/`
        *   `GET, PUT, PATCH, DELETE /api/v1/inventory/fabrics/{id}/`
    *   **Accessories:**
        *   `GET, POST /api/v1/inventory/accessories/`
        *   `GET, PUT, PATCH, DELETE /api/v1/inventory/accessories/{id}/`

*   **Orders:**
    *   `GET, POST /api/v1/orders/`
    *   `GET, PUT, PATCH, DELETE /api/v1/orders/{id}/`
    *   Order creation supports nested `items` (OrderItems).
    *   File uploads for `voice_note` and `design_image` are part of Order create/update (use `multipart/form-data`).
    *   **Nested Payments:**
        *   `GET, POST /api/v1/orders/{order_pk}/payments/`
        *   `GET, PUT, PATCH, DELETE /api/v1/orders/{order_pk}/payments/{id}/`

**Note on API Usage:**
*   Most endpoints require authentication (Bearer token in Authorization header).
*   List endpoints support pagination, searching (`?search=...`), and ordering (`?ordering=...`).
*   Refer to the detailed API Contract document (from Phase 2) for specific request/response body structures and status codes.

## File Uploads

*   Order voice notes and design images can be uploaded when creating or updating an Order.
*   Use `multipart/form-data` for requests that include file uploads.
*   Files are stored in the `mediafiles/` directory during development. For production, configure external storage (e.g., S3).

## Running Tests (Placeholder)

```bash
python manage.py test
# Specific app tests:
# python manage.py test orders
# python manage.py test customers
```
(No tests have been written yet, but this is where the command would go.)

---
This backend provides a solid foundation for the DarziFlow application. For detailed API specifications, please refer to the API contract documentation.
```
