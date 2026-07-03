# Food Delivery API — Interview Preparation Guide

This document is my personal preparation reference for the final interview. It walks
through the original task, what the reviewers are really looking for, the technology
choices I made and why, the API architecture and request flow, a module-by-module tour
of the codebase, how to run and test everything, and finally a set of talking scripts I
can use to present the project confidently in roughly 20–25 minutes.

---

## Table of Contents

1. [Project Requirements (as delivered by Toptal)](#1-project-requirements-as-delivered-by-toptal)
2. [Summary, Key Points, and What the Reviewers Want](#2-summary-key-points-and-what-the-reviewers-want)
3. [Technology Stack and Why I Chose It](#3-technology-stack-and-why-i-chose-it)
4. [API Architecture and Request Flow](#4-api-architecture-and-request-flow)
5. [Feature Implementation, File by File](#5-feature-implementation-file-by-file)
6. [Running and Testing the API](#6-running-and-testing-the-api)
7. [Talking Scripts for the Interview](#7-talking-scripts-for-the-interview)

---

## 1. Project Requirements (as delivered by Toptal)

> The text below is reproduced exactly as it was provided in the task brief.

**Task: Food Delivery**
**Est. time/effort: 30 hours**

**Task scope and expectations**

Your task is to write a food delivery service API.

You need to write an API for a simple application where users can order meals from restaurants.

The user must be able to create an account and log in using the API.

Implement 2 roles with different permission levels:

- **Customer:** Can see all restaurants and place orders from them.
- **Restaurant Owner:** Can CRUD restaurants and meals.

Each user can have only one account (the user is identified by an email).

A restaurant should have a name and description of the type of food they serve.

A meal should have a name, description, and price.

Orders include a list of meals, date, total amount, and status.

An order should be placed for a single restaurant only, but it can have multiple meals.

Orders can also contain a custom tip amount and can reference a coupon for a percentage discount.

There is no need to handle payment of any kind or even to simulate payment handling.

Restaurant owners and customers can change the order status respecting the below flow and permissions:

- **Placed:** Once a customer places an order.
- **Canceled:** If the customer or restaurant owner cancels the order.
- **Processing:** Once the restaurant owner starts to make the meals.
- **In Route:** Once the meal is finished and the restaurant owner marks it's on the way.
- **Delivered:** Once the restaurant owner receives information that the meal was delivered by their staff.
- **Received:** Once the customer receives the meal and marks it as received.

Orders should have a history of the date and time of the status change.

Customers should be able to browse their order history and view updated order status.

Customers and restaurant owners should be able to see a list of the orders.

**Implement Administrator Role**

An administrator who can CRUD users (of any role), restaurants, and meals and change all
user/restaurant/meal information, including blocking.

The application should include one built-in admin account that cannot be deleted.

REST/GraphQL API. Make it possible to perform all user and admin actions via the API,
including authentication.

In any case, you should be able to explain how a REST/GraphQL API works and demonstrate
that by creating functional tests that use the REST/GraphQL Layer directly. Please be
prepared to use REST/GraphQL clients like Postman, cURL, etc., for this purpose.

**Milestones and task delivery**

The deadline to submit the completed project is 7 days from the moment the requirements
are received. Code must be committed at least six hours before the meeting, and the final
interview must be attended on time.

---

## 2. Summary, Key Points, and What the Reviewers Want

### In plain terms

The task is to build the **backend API for a food delivery platform**. There is no
frontend requirement — everything is exercised over HTTP through the API itself, tests,
and tools like Postman, cURL, or Swagger. The domain is small but the rules are real:
three roles with different powers, a strict order lifecycle, and an administrator who can
manage everything.

### The core entities

- **User** — identified by email, with one of three roles: Customer, Restaurant Owner, Administrator.
- **Restaurant** — has a name and description, belongs to one owner, can be blocked.
- **Meal** — has a name, description, and price, and belongs to one restaurant, can be blocked.
- **Order** — belongs to one customer and exactly one restaurant, contains multiple meals,
  carries a status, a tip amount, an optional coupon, and a calculated total.
- **OrderItem** — a single meal line on an order, storing the quantity and the price at the time of ordering.
- **OrderStatusHistory** — an audit trail recording every status change, who made it, and when.
- **Coupon** — a code with a percentage discount that can be applied to an order.

### The key features the reviewers will check

- **Authentication over the API** — register and log in, receive tokens, use them on every request.
- **Role-based permissions** — customers, owners, and admins each see and do only what they should.
- **Restaurant and meal management** — owners manage their own; admins manage everyone's.
- **Order placement** — single restaurant per order, multiple meals, tip, coupon, correct total.
- **Order state machine** — the exact Placed → Processing → In Route → Delivered → Received
  flow, plus cancellation, with the right role allowed to make each move.
- **Status history** — every transition recorded with a timestamp and the actor.
- **Scoped listings** — customers see their own orders, owners see orders for their restaurants, admins see all.
- **Administrator role** — full CRUD over users, restaurants, meals, and coupons, including blocking.
- **Built-in, undeletable admin** — ships with the app and is protected at two layers.
- **Functional tests through the REST layer** — proving the API works end to end.

### The skills the reviewers are really evaluating

Beyond "does it work", a Toptal screening looks at engineering judgment: clean separation
of concerns, sensible data modeling, security-minded permission design, a domain rule
(the state machine) implemented correctly and defensively, meaningful tests that hit the
real HTTP layer, and the ability to explain all of it clearly. The brief explicitly says I
should be able to explain how a REST API works and demonstrate it live — so communication
and a smooth demo matter as much as the code.

---

## 3. Technology Stack and Why I Chose It

| Layer | Technology | Role in the project |
| --- | --- | --- |
| Language | Python 3.12 | Primary language |
| Web framework | Django 5 | Project structure, ORM, migrations, admin |
| API framework | Django REST Framework (DRF) | Serializers, viewsets, routers, permissions |
| Authentication | djangorestframework-simplejwt | Stateless JWT access/refresh tokens |
| API documentation | drf-spectacular | OpenAPI 3 schema and Swagger UI |
| Testing | pytest + pytest-django | Functional tests through the REST layer |
| Database | SQLite | Zero-config local persistence for the demo |

### Why Django and Django REST Framework

I have strong experience with Django, and for an API shaped like this one it is genuinely
the best fit, not just the familiar one. The domain is relational and CRUD-heavy —
users, restaurants, meals, orders, items, history, coupons — and Django's ORM and
migration system let me model those relationships cleanly and evolve them safely. Django
REST Framework then sits on top and gives me exactly the building blocks this task needs:
serializers for validation and representation, viewsets and routers to expose consistent
RESTful resources with very little boilerplate, and a composable permission system that
maps directly onto the role rules in the brief. Because so much is provided and
well-tested by the framework, I could spend my time on the parts that actually carry the
business value — the order state machine, the permission boundaries, and the tests —
rather than on plumbing.

### Why SimpleJWT for authentication

The requirement is that authentication happens over the API. Stateless JWT is the natural
choice for that: the client logs in once, receives an access and a refresh token, and then
sends the access token as a bearer token on every subsequent request. There is no
server-side session to manage, which keeps the API clean and horizontally scalable.
SimpleJWT integrates directly with DRF's authentication layer, and I extended its token
serializer to embed the user's role and email into the token payload, which makes the
token self-descriptive and convenient on the client side.

### Why drf-spectacular for documentation

The brief asks me to demonstrate the API with tools like Postman and cURL, and to be able
to explain how a REST API works. drf-spectacular generates an OpenAPI 3 schema straight
from the code and serves an interactive Swagger UI. That gives the reviewer a live,
browsable contract of every endpoint, and it lets me authorize once and try calls right in
the browser during the demo.

### Why pytest with pytest-django

The task specifically calls for functional tests that use the REST layer directly. pytest
keeps tests concise and readable, and pytest-django plus DRF's `APIClient` let each test
fire real HTTP requests at the API and assert on real HTTP responses and status codes.
That is exactly the kind of test the brief is asking for — not isolated unit tests of
functions, but tests that prove the endpoints behave correctly through the same interface a
real client would use.

### Why SQLite

For a screening project that the reviewer needs to clone and run in minutes, SQLite is the
pragmatic choice: it needs zero setup and ships as a single file. Because everything goes
through Django's ORM, moving to PostgreSQL for production is purely a settings change — no
application code is tied to the database engine. I keep the database file under a dedicated
`data/` directory created at startup.

---

## 4. API Architecture and Request Flow

### High-level architecture

The application is a standard layered Django REST Framework service. A request enters
through Django's URL routing, passes through authentication and permission checks, reaches
a viewset, which delegates validation and representation to a serializer, and — for the
non-trivial order operations — defers the actual business logic to a dedicated service
module. Persistence is handled by Django's ORM.

```
                         HTTP request (JSON + Bearer token)
                                      |
                                      v
                         +---------------------------+
                         |   config/urls.py routing  |
                         |  /api/... -> app routers  |
                         +---------------------------+
                                      |
                                      v
                         +---------------------------+
                         |  Authentication (JWT)     |   <- SimpleJWT decodes the token
                         |  identifies request.user  |      and identifies the user
                         +---------------------------+
                                      |
                                      v
                         +---------------------------+
                         |  Permission classes       |   <- IsAuthenticated, IsNotBlocked,
                         |  role + blocked checks     |      IsCustomer / IsOwner / IsAdmin
                         +---------------------------+
                                      |
                                      v
                         +---------------------------+
                         |  ViewSet / View           |   <- queryset scoping per role,
                         |  (accounts/restaurants/   |      action -> serializer selection
                         |   orders)                 |
                         +---------------------------+
                            |                    |
                            v                    v
              +-----------------------+   +-------------------------+
              |  Serializer           |   |  Service layer          |
              |  validation +         |   |  orders/services.py     |
              |  representation +      |   |  place_order(),         |
              |  field-level locking  |   |  transition_order_status|
              +-----------------------+   +-------------------------+
                            |                    |
                            +----------+---------+
                                       v
                         +---------------------------+
                         |  Django ORM / Models      |
                         |  Users, Restaurants,      |
                         |  Meals, Orders, Items,    |
                         |  StatusHistory, Coupons   |
                         +---------------------------+
                                       |
                                       v
                              +-----------------+
                              |  SQLite database |
                              +-----------------+
                                       |
                                       v
                          HTTP response (JSON + status code)
```

### The three apps and their responsibilities

The project is deliberately split into three focused Django apps, each owning one slice of
the domain:

- **`accounts`** — the custom user model, authentication (register, login, refresh, me),
  and admin user management.
- **`restaurants`** — restaurants and meals, with owner/admin management and public browsing.
- **`orders`** — orders, order items, status history, coupons, and the order state machine.

### Order status state machine

The heart of the domain is the order lifecycle. I modeled it as an explicit state machine
in `orders/services.py`, where the allowed transitions and the roles permitted to trigger
each one are declared as data, not scattered through `if` statements.

```
        (customer places order)
                  |
                  v
             +---------+      owner       +------------+      owner      +-----------+
             | PLACED  | ---------------> | PROCESSING | --------------> | IN_ROUTE  |
             +---------+                  +------------+                 +-----------+
                  |                             |                              |
                  | customer/owner              | customer/owner               | owner
                  v                             v                              v
             +----------+                  +----------+                  +-----------+
             | CANCELED |                  | CANCELED |                  | DELIVERED |
             +----------+                  +----------+                  +-----------+
                                                                              |
                                                                              | customer
                                                                              v
                                                                        +-----------+
                                                                        | RECEIVED  |
                                                                        +-----------+
```

In words: an order starts as **Placed**. From Placed or Processing it can be **Canceled**
by either the customer or the owner. The owner drives it forward through **Processing** and
**In Route**, then marks it **Delivered**. Finally the customer confirms by marking it
**Received**. Once an order is In Route it can no longer be canceled, and every move is
restricted to the correct role. Each successful transition writes a row into the order's
status history with the actor and a timestamp.

### How this architecture meets the requirements

Every requirement in the brief maps onto a concrete part of this design. Authentication
over the API is handled by the JWT layer and the `accounts` auth endpoints. The two
required roles plus the administrator are enforced by the permission classes and the
per-role queryset scoping in each viewset. Restaurants and meals, with their owner/admin
CRUD rules, live in the `restaurants` app. Orders being tied to a single restaurant with
multiple meals, a tip, and a coupon is enforced inside `place_order`, which also computes
the total. The exact status flow and its permissions are the state machine in the service
layer, and the status history requirement is satisfied by writing an `OrderStatusHistory`
row on every transition. Scoped listings come from `get_queryset` in each viewset. The
administrator's full control and the undeletable built-in admin are handled in the
`accounts` app and a data migration. And the whole thing is demonstrable through the REST
layer via tests, Postman, cURL, and Swagger — which is precisely what the brief asks for.

---

## 5. Feature Implementation, File by File

This section maps each feature to the files that implement it, so I can navigate the code
confidently and explain any part on request.

### 5.1 The custom user model and roles

**Files:** `accounts/models.py`, `accounts/migrations/0001_initial.py`

I use a custom user model based on `AbstractBaseUser` and `PermissionsMixin`, with email as
the unique identifier instead of a username — exactly what the brief requires ("the user is
identified by an email"). The `Role` is a `TextChoices` enum with `customer`, `owner`, and
`admin`. Convenience properties (`is_customer`, `is_owner`, `is_admin`) keep role checks
readable across the codebase. A custom `UserManager` provides `create_user` and
`create_superuser`. The model also has `is_blocked` (for the blocking requirement) and
`is_builtin_admin` (to mark the protected account).

Why a custom user model: deciding this up front is a well-known Django best practice,
because switching later is painful. Email-as-identifier is a direct requirement, and
carrying `role` on the user keeps authorization simple and fast.

### 5.2 The undeletable built-in admin

**Files:** `accounts/models.py` (the `delete` override), `accounts/migrations/0002_create_builtin_admin.py`, `accounts/views.py` (the `destroy` override)

The built-in admin is protected at **two layers**, which is a point I want to highlight as
defense in depth. First, at the model layer: `User.delete()` raises `ProtectedError` if the
account is flagged as the built-in admin, so it cannot be deleted from anywhere in the code,
including the Django admin or a shell. Second, at the API layer: `UserViewSet.destroy`
returns `403 Forbidden` with a clear message before it ever reaches the model. The account
itself is created by an **idempotent data migration**, so it ships with the database and
re-running migrations never duplicates or overwrites it.

### 5.3 Authentication: register, login, refresh, me

**Files:** `accounts/views.py`, `accounts/serializers.py`, `accounts/serializers_jwt.py`, `accounts/urls.py`

- **Register** (`POST /api/auth/register/`) — open to anyone, creates a Customer account.
  Implemented with `RegisterSerializer`, which enforces a minimum password length and
  hashes the password through `create_user`.
- **Login** (`POST /api/auth/login/`) — returns JWT access and refresh tokens. I subclass
  SimpleJWT's view and serializer so the token payload also carries the user's role and
  email. I added an explicit pre-check that returns `403` for blocked users with a clear
  message rather than a generic failure.
- **Refresh** (`POST /api/auth/refresh/`) — exchanges a refresh token for a new access token.
- **Me** (`GET /api/auth/me/`) — returns the authenticated user's profile, and is itself
  guarded by `IsAuthenticated` and `IsNotBlocked`.

### 5.4 Permission classes

**Files:** `accounts/permissions.py`, `restaurants/permissions.py`, and `config/settings.py` (defaults)

The role rules are expressed as small, composable DRF permission classes:

- `IsNotBlocked` — applied globally as a default, so a blocked user is shut out everywhere.
- `IsCustomer`, `IsOwner`, `IsAdmin` — each checks authentication, not-blocked, and the
  specific role.
- `RestaurantPermission` and `MealPermission` — object-level permissions that allow safe
  (read) methods to anyone authenticated, allow admins everything, and otherwise restrict
  writes to the owner of the resource.

The global default in settings is `IsAuthenticated` plus `IsNotBlocked`, so every endpoint
is locked down unless it explicitly opts out (as register and login do). This "secure by
default" posture is deliberate.

### 5.5 Restaurants and meals

**Files:** `restaurants/models.py`, `restaurants/serializers.py`, `restaurants/views.py`, `restaurants/urls.py`

Restaurants and meals are exposed as DRF `ModelViewSet`s wired through a router, giving
full CRUD with standard REST URLs. The interesting logic is in two places:

- **Queryset scoping** (`get_queryset`): customers and the public only ever see
  non-blocked restaurants and meals; owners see their own for management but only active
  ones when browsing; admins see everything. This is how blocking is enforced on reads.
- **Serializer field locking** (`__init__` overrides): for non-admins, the `owner` and
  `is_blocked` fields are made read-only, so an owner cannot reassign their restaurant to
  someone else or unblock themselves. When an owner creates a restaurant, ownership is set
  automatically to the current user; when an admin creates one, they must specify an owner,
  which is validated explicitly.

The meal serializer also validates that an owner can only attach meals to their own
restaurants, while admins are exempt.

### 5.6 Orders, order items, and the service layer

**Files:** `orders/models.py`, `orders/serializers.py`, `orders/views.py`, `orders/services.py`, `orders/urls.py`

This is the richest part of the project. The models capture the full shape required by the
brief: an `Order` tied to one customer and one restaurant, with a status, tip, optional
coupon, and total; `OrderItem` lines that store the quantity and the unit price at the time
of ordering (so historical orders stay accurate even if a meal's price later changes); and
`OrderStatusHistory` rows for the audit trail.

The key design decision is the **service layer** in `orders/services.py`. Rather than
stuffing business logic into the views, I isolated it into two functions:

- `place_order(...)` — runs inside a database transaction. It validates the restaurant is
  available, that there is at least one item, that the coupon (if any) is valid and active,
  and crucially that **every requested meal belongs to that one restaurant and is
  available**. It computes the subtotal, applies the percentage discount, adds the tip,
  creates the order and its items in bulk, and records the initial "Placed" history entry.
- `transition_order_status(...)` — also transactional. It checks the move is allowed by the
  state machine, that the acting user's role is permitted to make that move, and that the
  user actually owns the order or the restaurant involved. Then it updates the status and
  appends a history row.

The `OrderViewSet` selects a different serializer per action — a create serializer for
placing orders, a small status serializer for transitions, and a rich read serializer that
nests items and history. Both `PUT` and `PATCH` on an order are routed to the same status
transition logic, because an order isn't a freely editable resource — the only mutation
allowed is a controlled status change. Coupons are managed through an admin-only viewset.

Putting the rules in a service layer keeps the views thin, makes the logic reusable (the
demo seed command calls the same functions), and makes the behavior easy to test directly.

### 5.7 Order listing scope

**File:** `orders/views.py` (`get_queryset`)

The listing rules from the brief are enforced here: a customer sees only their own orders,
an owner sees only orders placed at their restaurants, and an admin sees all orders. The
queryset also uses `select_related` and `prefetch_related` to avoid N+1 queries when
serializing nested items and history — a small but real performance consideration.

### 5.8 Configuration and documentation endpoints

**Files:** `config/settings.py`, `config/urls.py`

Settings wire up the custom user model, the JWT lifetimes, the DRF defaults (JWT auth plus
the secure-by-default permissions), and drf-spectacular. The root URL config mounts the
three apps under `/api/`, the Django admin under `/admin/`, the OpenAPI schema at
`/api/schema/`, and Swagger UI at `/api/docs/`.

### 5.9 Demo seed command

**File:** `accounts/management/commands/seed_demo.py`

A custom management command, `python manage.py seed_demo`, populates the database with two
restaurant owners, their restaurants and meals, a returning customer with one fully
completed order, and a coupon. It deliberately leaves one customer unregistered so I can
demonstrate live sign-up during the interview. It's idempotent and reuses the same service
functions the API uses, so the seeded data is created through exactly the same code path as
real orders.

### 5.10 Tests

**Files:** `accounts/tests/`, `restaurants/tests/`, `orders/tests/`

There are around 40 functional tests, all driving the real REST layer through DRF's
`APIClient`. They cover registration and login (including blocked users), the user model
and the protected built-in admin, admin user and coupon management, restaurant and meal
catalog rules (blocking, ownership, admin overrides), and the full order lifecycle —
placing orders, totals with tip and coupon, rejecting meals from other restaurants, the
complete status flow, cancellation rules, role restrictions, and per-role list scoping.
These are exactly the "functional tests that use the REST layer directly" the brief asks
for.

---

## 6. Running and Testing the API

### Prerequisites

- Python 3.12
- pip and virtualenv

### Step 1 — Clone and enter the project

```bash
git clone https://git.toptal.com/screening-ops/Daksh-sharma.git
cd Daksh-sharma
```

### Step 2 — Create and activate a virtual environment

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 — Apply migrations

This creates the database **and** the built-in admin account.

```bash
python manage.py migrate
```

### Step 5 — (Optional) Seed demo data

```bash
python manage.py seed_demo
```

This creates:

- Owners: `messi@worldcup.com`, `yamal@worldcup.com` (password `password123`)
- Customer: `fan_john@worldcup.com` (password `password123`)
- A coupon `WELCOME15` (15% off) and a completed sample order.

### Step 6 — Run the server

```bash
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/`.

### Built-in admin credentials

```
email:    admin@fooddelivery.local
password: Admin12345!
```

### Running the tests

```bash
pytest            # run everything
pytest -q         # one-line summary
pytest -v         # list every test
```

### Key endpoints at a glance

| Method | Endpoint | Who | Purpose |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Public | Create a customer account |
| POST | `/api/auth/login/` | Public | Get access + refresh tokens |
| POST | `/api/auth/refresh/` | Public | Refresh the access token |
| GET | `/api/auth/me/` | Authenticated | Current user profile |
| GET/POST/PATCH/PUT/DELETE | `/api/users/` | Admin | Manage users (any role) |
| GET/POST/PATCH/PUT/DELETE | `/api/restaurants/` | Owner/Admin write, all read | Manage/browse restaurants |
| GET/POST/PATCH/PUT/DELETE | `/api/meals/` | Owner/Admin write, all read | Manage/browse meals |
| GET/POST/PATCH | `/api/orders/` | Role-scoped | Place, list, view, transition orders |
| GET/POST/PATCH/PUT/DELETE | `/api/coupons/` | Admin | Manage coupons |
| GET | `/api/docs/` | Public | Swagger UI |
| GET | `/api/schema/` | Public | OpenAPI schema |

### Trying it with cURL

```bash
# 1. Log in and capture the access token
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"fan_john@worldcup.com","password":"password123"}'

# 2. Use the token on a protected endpoint
curl http://127.0.0.1:8000/api/restaurants/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Trying it with Postman

A ready-to-import collection and environment live under `docs/postman/`:

- `docs/postman/food-delivery.postman_collection.json`
- `docs/postman/food-delivery.postman_environment.json`

Import both, select the **Food Delivery - Local** environment, run **Auth → Login** first
(the token is captured automatically and reused), then work through the folders. IDs created
along the way are chained between requests, so there's no manual copying.

### Trying it with Swagger

1. Open `http://127.0.0.1:8000/api/docs/`.
2. Call `POST /api/auth/login/` and copy the `access` token.
3. Click **Authorize** and enter `Bearer <access-token>`.
4. Try any endpoint directly from the browser.

---

## 7. Talking Scripts for the Interview

These are written to be spoken naturally, in a continuous, conversational way. Together they
run about 20–25 minutes at a comfortable pace. I can pause for questions between sections.

### 7.1 Introduction (about 1.5 minutes)

"Thanks for taking the time today. To introduce myself briefly — I'm a senior software
engineer with over seven years of experience, and most of that has been spent building and
maintaining backend systems and APIs, a lot of it in Python and Django. I've worked across
the stack, but the backend and API design is really where I'm most at home: data modeling,
authentication and authorization, designing clean REST interfaces, and making sure the
business rules are correct and well tested. I enjoy taking a fuzzy set of requirements and
turning it into a system that's simple to reason about and safe to extend. For this project
I built the food delivery API end to end, and I'm happy to walk you through how I
approached it, show you the code, and then demo it live however you'd prefer — manually, in
Postman, or through Swagger."

### 7.2 Project understanding (about 2 minutes)

"Let me start by playing back my understanding of the task, just to make sure we're aligned.
The goal was to build the backend API for a food delivery service — there's no frontend
involved, everything is done over HTTP. There are three kinds of users: customers, who
browse restaurants and place orders; restaurant owners, who manage their own restaurants and
meals and move orders along; and an administrator, who can manage everything in the system,
including blocking users, restaurants, and meals. Users are identified by email, and each
person has a single account.

The interesting domain rule is the order lifecycle. An order is always for one restaurant
but can contain several meals, it can carry a tip and a percentage-discount coupon, and it
moves through a specific sequence of statuses — placed, processing, in route, delivered,
received — with cancellation possible early on. Each of those transitions is restricted to
a particular role, and the system has to keep a full history of when each change happened
and who made it. On top of that, there has to be one built-in admin account that can never
be deleted, and the whole thing has to be demonstrable directly through the API with
functional tests and tools like Postman. That last point shaped a lot of my decisions —
I treated the API itself as the product."

### 7.3 Technology choices (about 3 minutes)

"For the stack, I chose Python with Django and Django REST Framework, and I want to explain
why, because it wasn't just familiarity — though I do have strong experience with Django.
The domain here is very relational and CRUD-heavy: users, restaurants, meals, orders, order
items, status history, coupons, all with clear relationships between them. Django's ORM and
migration system are excellent for exactly that — I can model those relationships cleanly
and evolve the schema safely. Django REST Framework then gives me serializers for validation
and representation, viewsets and routers for consistent REST endpoints with very little
boilerplate, and — most importantly for this task — a composable permission system that maps
almost one-to-one onto the role rules in the brief. So the framework handles the plumbing,
and I get to spend my time on what actually carries the value: the order state machine, the
permission boundaries, and the tests.

For authentication I used JSON Web Tokens via SimpleJWT, because the requirement is that
auth happens over the API. JWT is stateless — the client logs in once, gets an access and a
refresh token, and sends the access token as a bearer token on each request. There's no
server-side session to manage, which keeps things clean and scalable. I extended the token
to also carry the user's role and email so it's self-descriptive.

For documentation I used drf-spectacular, which generates an OpenAPI schema from the code
and serves a live Swagger UI — that's both great for the reviewer and handy for the demo.
For testing I used pytest with DRF's API client, so my tests fire real HTTP requests at the
API, which is exactly the functional testing the brief asked for. And I kept the database
as SQLite for the screening so it runs with zero setup — but because everything goes through
the ORM, switching to PostgreSQL for production is just a settings change, no code changes."

### 7.4 Architecture and workflow (about 4 minutes)

"Let me describe the architecture and how a request flows through it. It's a clean layered
design. A request comes in as JSON with a bearer token. Django's URL routing sends it to the
right app — I split the project into three focused apps: accounts for users and auth,
restaurants for restaurants and meals, and orders for orders, coupons, and the state
machine. Before the request reaches any logic, the JWT authentication layer decodes the
token and identifies the user, and then the permission classes run. I made the system secure
by default — globally, every endpoint requires an authenticated, non-blocked user, and
endpoints have to explicitly opt out of that, like register and login do. On top of that I
have small, composable permission classes for customer, owner, and admin roles, plus
object-level permissions that ensure an owner can only touch their own restaurants and
meals.

Once past permissions, the request hits a viewset. Two things happen there that I think are
worth calling out. First, queryset scoping — each viewset filters what you can even see
based on your role. A customer only sees non-blocked restaurants and only their own orders;
an owner sees orders for their restaurants; an admin sees everything. So authorization isn't
only about what you can do, it's also about what data exists for you. Second, the viewset
picks the right serializer for the action — for example, placing an order uses a different
serializer than reading one back.

For the complex operations — placing an order and transitioning its status — I deliberately
pushed the logic out of the views and into a dedicated service module. This is the part I'm
most deliberate about. The order lifecycle is a real state machine, and I modeled it as
data: a dictionary of which statuses can follow which, and another of which roles are
allowed to make each move. So when someone tries to move an order, the service checks three
things — is this transition allowed at all, is this user's role permitted to make it, and
does this user actually own the order or the restaurant. Both placing and transitioning run
inside database transactions, so we never end up with a half-created order. And every
successful transition writes a history record with the actor and timestamp, which satisfies
the audit-trail requirement. Keeping this in a service layer means the views stay thin, the
logic is reusable — my demo seed command calls the exact same functions — and it's very easy
to test directly. Every requirement in the brief maps onto a specific place in this design,
which is something I was intentional about."

### 7.5 Manual demo walkthrough (about 4 minutes)

"Let me show it working. I'll start the server with `python manage.py runserver`. The
database already has the built-in admin from a data migration, and I've seeded some demo
data with `python manage.py seed_demo` — a couple of restaurant owners with their menus, a
customer, and a coupon.

First I'll show registration and login. I'll register a brand-new customer over the API,
and you'll see the response comes back with the customer role assigned automatically. Then
I'll log in with that account and you'll see I get back an access token and a refresh token.
That access token is what authorizes every following request as a bearer token.

Next, as that customer, I'll browse restaurants — and notice I only see active, non-blocked
ones. I'll place an order against one restaurant with a couple of meals, add a tip, and apply
the coupon, and you'll see the API calculates the total correctly: it discounts the subtotal
by the coupon percentage and then adds the tip. The order comes back as 'placed', with a
history entry already recorded.

Then I'll switch hats. I'll log in as the restaurant owner and move that order forward —
processing, then in route, then delivered. If I try to skip a step or make a move I'm not
allowed to, the API rejects it with a clear error. Finally I log back in as the customer and
mark the order received. If we look at the order now, the status history shows the full
timeline with who did what and when. And just to show the admin powers, I'll log in as the
built-in admin and block a user or a restaurant, and try to delete the built-in admin
account — which the API refuses, because that account is protected at both the model and the
API layer."

### 7.6 Postman demo walkthrough (about 3 minutes)

"I've also included a Postman collection and environment in the repo under docs/postman, so
this is repeatable and easy to follow. I'll import both files and select the 'Food Delivery
- Local' environment in the top right. The collection is organized into folders — Auth,
Admin Users, Restaurants, Meals, Coupons, and Orders.

The nice part is that it's wired together. I run the Login request first, and the access
token is captured automatically into an environment variable, so every other request reuses
it without me copying anything by hand. As I create resources — a restaurant, a meal, an
order — their IDs get chained into variables too, so the later requests just work. I'll walk
through placing an order and then transitioning its status. One thing to note is that the
status changes are role-specific, so for the owner-driven steps I re-run the owner login,
and for the customer's 'received' step I log back in as the customer — the collection is set
up to make that switch easy. This gives you a clean, reproducible way to exercise the entire
API without touching the code."

### 7.7 Swagger demo walkthrough (about 2 minutes)

"Finally, the API documents itself. If I open `/api/docs/`, there's a full Swagger UI
generated from the code by drf-spectacular, so it's always in sync with the actual
endpoints. Every resource is listed with its methods, parameters, and request and response
schemas — it's effectively a live contract for the API.

To use the authenticated endpoints here, I call the login endpoint right in Swagger, copy
the access token from the response, click Authorize at the top, and paste it in as a bearer
token. From then on I can try any endpoint directly in the browser — list restaurants, place
an order, transition a status — and see the real responses and status codes. This is also a
great way to explain how a REST API works to anyone, because you can see the verbs, the
resource URLs, the request bodies, and the status codes all in one place. So between the
functional tests, cURL, Postman, and Swagger, every action in the system is fully
demonstrable through the API — which was the core expectation of the task."

### 7.8 Optional closing line

"That's the full picture — the architecture, the key decisions, and the system working end
to end. I'm happy to go deeper into any part, whether that's the permission design, the
order state machine, the tests, or how I'd take this toward production. What would you like
to dig into?"

---

*Prepared by Daksh Sharma for the Food Delivery API final interview.*
