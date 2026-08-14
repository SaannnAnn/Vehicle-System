# Vehicle Inventory & Booking REST API

A Django REST Framework backend for managing a vehicle fleet and rental bookings, with
built-in validation for date overlaps, past-dated bookings, phone numbers, and
auto-calculated pricing.

## Tech Stack

- Python 3
- Django 6.1
- Django REST Framework
- django-filter (query param filtering)
- SQLite by default (Postgres-ready via `DATABASE_URL`)

## Project Structure

```
vehicle_system/
├── vehicle_system/       # Project settings, root urls
├── inventory/             # App: models, serializers, views, urls, admin
├── requirements.txt
├── .env.example
└── manage.py
```

## 1. Setup Steps

### Clone and enter the project
```bash
git clone <your-repo-url>
cd vehicle_system
```

### Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## 2. Installation Guide (Environment Variables)

Copy the example env file and edit as needed:
```bash
cp .env.example .env
```

`.env` variables:

| Variable        | Description                                              | Default                    |
|-----------------|------------------------------------------------------------|-----------------------------|
| `SECRET_KEY`    | Django secret key                                          | dev placeholder (insecure) |
| `DEBUG`         | Debug mode                                                  | `True`                     |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts                       | `localhost,127.0.0.1`      |
| `DATABASE_URL`  | Full DB connection string. Leave unset to use local SQLite.| SQLite `db.sqlite3`        |

To use Postgres instead of SQLite, set in `.env`:
```
DATABASE_URL=postgres://vehicle_user:vehicle_password@localhost:5432/vehicle_system_db
```

## 3. Migration Commands

```bash
python manage.py makemigrations
python manage.py migrate
```

Optional — create an admin user to use the Django admin panel:
```bash
python manage.py createsuperuser
```

## 4. How to Run the Project

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`
Django admin is available at `http://127.0.0.1:8000/admin/`

## 5. How to Test the APIs

You can test using **Postman**, **curl**, or the **Django REST Framework browsable
API** (just open any endpoint URL in your browser, e.g.
`http://127.0.0.1:8000/api/vehicles/`).

Example with curl — create a vehicle:
```bash
curl -X POST http://127.0.0.1:8000/api/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Swift","brand":"Maruti","year":2023,"price_per_day":"1500.00","fuel_type":"Petrol"}'
```

Example with curl — create a booking:
```bash
curl -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"vehicle":1,"customer_name":"Sandra","customer_phone":"9876543210","start_date":"2026-09-01","end_date":"2026-09-04"}'
```

You can also run Django's test client / add your own tests in `inventory/tests.py`
and execute:
```bash
python manage.py test
```

## 6. API Endpoint List

### Vehicle Endpoints

| Method | Endpoint                | Description        |
|--------|--------------------------|---------------------|
| GET    | `/api/vehicles/`         | List all vehicles  |
| POST   | `/api/vehicles/`         | Add a new vehicle  |
| GET    | `/api/vehicles/<id>/`    | Vehicle details    |
| PUT    | `/api/vehicles/<id>/`    | Update a vehicle   |
| DELETE | `/api/vehicles/<id>/`    | Delete a vehicle   |

**Filtering** (query params, combinable):
- `/api/vehicles/?brand=Toyota`
- `/api/vehicles/?fuel_type=Electric`
- `/api/vehicles/?is_available=true`

### Booking Endpoints

| Method | Endpoint                | Description        |
|--------|--------------------------|---------------------|
| GET    | `/api/bookings/`         | List all bookings  |
| POST   | `/api/bookings/`         | Create a booking   |
| GET    | `/api/bookings/<id>/`    | Booking details    |

## 7. Business Logic / Booking Rules

- A vehicle **cannot be double-booked** — any overlapping date range for the same
  vehicle is rejected.
- `total_amount` is **auto-calculated** as `(end_date - start_date).days * price_per_day`
  and is a read-only field — clients cannot set it directly.
- `start_date` **cannot be in the past**.
- `end_date` **must be after** `start_date`.
- `customer_phone` **must be exactly 10 digits**.
- Once a booking is created, the associated vehicle's `is_available` flag is
  automatically set to `False`.

## 8. Sample JSON for Booking

Request — `POST /api/bookings/`
```json
{
  "vehicle": 1,
  "customer_name": "Sandra Rajan",
  "customer_phone": "9876543210",
  "start_date": "2026-09-01",
  "end_date": "2026-09-04"
}
```

Response — `201 Created`
```json
{
  "id": 1,
  "vehicle": 1,
  "vehicle_detail": {
    "id": 1,
    "name": "Swift",
    "brand": "Maruti",
    "year": 2023,
    "price_per_day": "1500.00",
    "fuel_type": "Petrol",
    "is_available": false
  },
  "customer_name": "Sandra Rajan",
  "customer_phone": "9876543210",
  "start_date": "2026-09-01",
  "end_date": "2026-09-04",
  "total_amount": "4500.00"
}
```

Validation error example — overlapping dates:
```json
{
  "non_field_errors": [
    "This vehicle is already booked for an overlapping date range."
  ]
}
```

## 9. Screen Recording

_Add your video file or a YouTube/Drive link here before submitting:_
`[Add link]`

## 10. Deployment

This project is ready to deploy on Render, Railway, PythonAnywhere, or any platform
supporting Django + Postgres. General steps:

1. Set `DEBUG=False` and a real `SECRET_KEY` and `ALLOWED_HOSTS` in the platform's
   environment variables.
2. Provision a Postgres database and set `DATABASE_URL`.
3. Add `gunicorn` (or the platform's preferred WSGI server) and a `Procfile`/start
   command, e.g. `gunicorn vehicle_system.wsgi`.
4. Run `python manage.py migrate` on deploy.
5. Serve static files (e.g. via `whitenoise`) since `DEBUG=False` disables Django's
   built-in static file serving.

_## Live API

https://your-api-name.onrender.com/api/
