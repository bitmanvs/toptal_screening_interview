# Food Delivery API

A REST backend for a simple food delivery service. Customers browse restaurants and place orders; restaurant owners manage their restaurants and meals; administrators manage users, restaurants, meals, and coupons, and can block any of them.

Built with Django and Django REST Framework. Authentication uses JWT. Every action, including authentication and all admin operations, is available over the HTTP API and is documented through Swagger.

**Roles**

- **Customer**: browse restaurants/meals, place orders, track and receive them.
- **Restaurant Owner**: full CRUD over their own restaurants and meals, and manage the status of orders placed at their restaurants.
- **Administrator**: CRUD over users (any role), restaurants, meals, and coupons, including blocking. A built-in admin account ships with the app and cannot be deleted.

## Tech stack

- Python 3.12
- Django 5 / Django REST Framework
- SimpleJWT (authentication)
- drf-spectacular (OpenAPI / Swagger)
- pytest (tests)
- SQLite (local database)

## Getting started

**1. Clone the repository**

```bash
git clone https://git.toptal.com/screening-ops/Daksh-sharma.git
cd Daksh-sharma
```

**2. Create and activate a virtual environment**

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Apply migrations**

This creates the database and the built-in admin account.

```bash
python manage.py migrate
```

**5. Run the server**

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/`.

**Built-in admin credentials**

```
email:    admin@fooddelivery.local
password: Admin12345!
```

**Optional: seed demo data**

Loads two owners with restaurants and meals, a returning customer with a completed order, and a coupon (handy for trying the API quickly):

```bash
python manage.py seed_demo
```

## Running the tests

The project ships with functional tests that exercise the REST layer directly (auth, roles, restaurants, meals, orders, the order status flow, and admin actions).

Run the full suite with a single command:

```bash
pytest
```

For a quieter summary or per-test output:

```bash
pytest -q      # one-line summary
pytest -v      # list every test
```

## Trying the API with Postman

A ready-to-import collection and environment are included under `docs/postman/`.

1. Start the server: `python manage.py runserver`
2. In Postman, **Import** both files:
   - `docs/postman/food-delivery.postman_collection.json`
   - `docs/postman/food-delivery.postman_environment.json`
3. Select the **Food Delivery - Local** environment (top-right).
4. Run **Auth → Login** first. The access token is captured automatically and reused by every other request.
5. Work through the folders (Auth, Admin - Users, Restaurants, Meals, Coupons, Orders). Created IDs (restaurant, meal, order) are chained between requests, so you don't have to copy them by hand.

Order-status changes are role-specific, so re-run the matching Login (owner for processing/in_route/delivered, customer for received) before those requests.

## Trying the API with Swagger

Interactive API docs are generated automatically.

- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **OpenAPI schema:** `http://127.0.0.1:8000/api/schema/`

To call authenticated endpoints from Swagger:

1. Call `POST /api/auth/login/` with your email and password and copy the `access` token from the response.
2. Click **Authorize** (top right) and enter `Bearer <access-token>`.
3. You can now try any endpoint directly from the browser.

## Authentication flow

1. `POST /api/auth/register/` creates a new customer account.
2. `POST /api/auth/login/` returns `access` and `refresh` tokens.
3. Send `Authorization: Bearer <access-token>` on every protected request.
4. `POST /api/auth/refresh/` exchanges a refresh token for a new access token.

## Author

Daksh Sharma
