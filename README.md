# Reservation API (FastAPI)

A simple reservation system built with FastAPI and SQLAlchemy, featuring JWT auth, user management, email verification (in-memory), appointment slots, and admin utilities.

## Features

- JWT authentication (login to get bearer token)
- User registration and profile updates
- Email verification via one-time code (in-memory store)
- Appointment slots: doctors create, users book
- Admin endpoints to list/search users and reservations

## Tech Stack

- FastAPI, Uvicorn
- SQLAlchemy (PostgreSQL)
- Pydantic v2
- SMPT Mail
  

## Project Structure

```
reserveation/
  main.py
  db.py
  config.py
  models.py
  schemas.py
  routers/
    auth.py
    users.py
    email.py
    reserve.py
    admin.py
    doctor.py
```

## Setup

1. Python 3.13 (or 3.11/3.12 should also work)
2. Create a virtualenv and install deps:

```bash
python -m venv venv
venv\Scripts\activate  # on Windows
pip install -r requirements.txt 
# Or install minimal set:
pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-jose pydantic email-validator
# Or using pip install:
pip install -r requirements.txt
```

3. Environment

- Database (PostgreSQL): set the connection information in config.py file.
  - Install driver: `pip install psycopg2-binary`
- Also the reservation.db file is available for using SQLite database.
- Email sending uses Gmail SMTP in `routers/email.py`. Set valid credentials or use an app password.

4. Run server

```bash
uvicorn main:app --reload
fastapi dev main.py
fastapi run main.py
```

Visit Docs: http://127.0.0.1:8000/docs

## Database Models (summary)

- `Users`: id, first_name, last_name, email, username, hashed_password, phone_number, active, role
- `Reservations`: id, user_id, doctor_id, reservation_time, description, status

## Auth

- Token endpoint: `POST /users/token`
  - Body: form-data fields `username`, `password`
  - Response: `{ access_token, token_type }`
- Include `Authorization: Bearer <token>` for protected endpoints.

## Users API

- `POST /users/create_user/`
  - Body (JSON): `username, email, first_name, last_name, phone_number, password, role`
  - On success: sends a 4-digit verification code to the provided email and stores code in-memory.

- `PUT /users/email_verification/`
  - Auth required
  - Query: `code`
  - Uses email from JWT to verify
  - On success: marks user as `active = True`.

- `GET /users/information/` (auth)
  - Returns current user info.

- Profile updates (auth):
  - `PUT /users/change_first_name/{user_model.id}`
  - `PUT /users/change_last_name/{user_model.id}`
  - `PUT /users/change_phone_number/{user_model.id}`
  - `PUT /users/change_email/{user_model.id}`
  - `PUT /users/change_password`
  - `PUT /users/change_username/{user_model.id}`

## Email Verification

- In-memory storage in `routers/email.py`:
  - `store_verification_code(email, code, ttl_minutes=30)`
  - `verify_verification_code(email, code)` consumes on success

## Appointments

- Reserve consumer endpoints under `/reserve`:
  - `GET /reserve/available` (auth)
  - `POST /reserve/book/{slot_id}` (auth, user/admin)
  - `GET /reserve/my-appointments` (auth)

- Doctor endpoints under `/appointments`:
  - `POST /appointments/doctor/create-slot` (auth doctor/admin)
  - `GET /appointments/doctor/my-schedule` (auth doctor/admin)
  - `PUT /appointments/doctor/cancel-slot/{slot_id}` (auth doctor/admin)

## Admin

- Prefix `/admin` (auth, admin role):
  - `GET /admin/test`
  - `GET /admin/get_all_users`
  - `GET /admin/get_all_reservations`
  - `GET /admin/get_reservations_by_user/{user_id}`
  - `GET /admin/get_reservation_by_doctor/{doctor_id}`
  - `GET /admin/delete_user/{user_id}`
  - `GET /admin/delete_reservation/{reservation_id}`
  - `PUT /admin/block_user/{user_id}`
  - `GET /admin/search_user/{search_term}`
  - `PUT /admin/update_user_role/{user_id}`
  - `PUT /admin/update_reservation_status/{reservation_id}`
  - All of the APIEndpoints is also available in /docs, via swagger ui.

## Troubleshooting

- Email verification fails as "Invalid or expired verification code":
  - Ensure you are logged in and your token includes `email`.
  - Use the latest code, restart server after changes.
  - Verify the exact email matches the one used on registration (case/whitespace).
  - Codes expire after TTL or after successful verification.

- Gmail SMTP errors:
  - Use an App Password and 2FA.
  - Check less-secure apps policy (if applicable) and network rules.

- You must submit database information and email verification credentials before running the app.

## License

MIT License


