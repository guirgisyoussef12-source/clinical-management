# Clinical Management System API

A REST API for managing clinic appointments, built with Django REST Framework and JWT authentication.

## Features

- Role-based access: **Doctor**, **Patient**, **Receptionist**
- JWT authentication
- Doctor & patient profile management
- Appointment booking with conflict detection
- Role-restricted status updates

## Tech Stack

- Python 3.x / Django 6
- Django REST Framework
- PostgreSQL
- Simple JWT

## Setup

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd clinical-management-main
pip install -r requirements.txt
```

### 2. Create `.env` file

```env
SECRET_KEY=your-secret-key-here
DB_NAME=clinic_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

### 3. Run migrations & start server

```bash
python manage.py migrate
python manage.py runserver
```

## API Endpoints

### Auth

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| POST | `/api/accounts/register/` | Register as doctor or patient | Public |
| POST | `/api/accounts/login/` | Get access & refresh tokens | Public |
| POST | `/api/accounts/refresh/` | Refresh access token | Public |

**Register body:**
```json
{
  "username": "ahmed",
  "email": "ahmed@example.com",
  "password": "securepass",
  "role": "PATIENT"
}
```
> `role` accepts `DOCTOR` or `PATIENT` only. `RECEPTIONIST` accounts are created via the admin panel.

---

### Doctor Profile

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/accounts/doctors/me/` | Get own profile |
| PATCH | `/api/accounts/doctors/me/` | Create or update own profile |

**PATCH body:**
```json
{
  "phone": "01012345678",
  "date_of_birth": "1985-03-15",
  "specialization": "Cardiology",
  "work_hours": "9am-5pm"
}
```

---

### Patient Profile

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/accounts/patients/me/` | Get own profile |
| PATCH | `/api/accounts/patients/me/` | Create or update own profile |

**PATCH body:**
```json
{
  "phone": "01098765432",
  "date_of_birth": "1995-07-20",
  "address": "123 Main St, Cairo",
  "gender": "MALE"
}
```

---

### Appointments

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/api/appointments/` | All roles | List own appointments (receptionist sees all) |
| POST | `/api/appointments/` | All roles | Book appointment |
| GET | `/api/appointments/{id}/` | All roles | Get single appointment |
| PUT/PATCH | `/api/appointments/{id}/` | All roles | Update appointment |
| DELETE | `/api/appointments/{id}/` | Receptionist | Delete appointment |
| PATCH | `/api/appointments/{id}/update_status/` | Doctor, Receptionist | Change status |

**POST body (receptionist):**
```json
{
  "doctor_id": 1,
  "patient_id": 2,
  "appointment_date": "2026-09-01",
  "appointment_time": "10:00:00"
}
```

**POST body (patient — `patient_id` auto-assigned):**
```json
{
  "doctor_id": 1,
  "appointment_date": "2026-09-01",
  "appointment_time": "10:00:00"
}
```

**Update status body:**
```json
{
  "status": "COMPLETED"
}
```
> Status choices: `SCHEDULED`, `COMPLETED`, `CANCELED`, `NO_SHOW`

---

## Permissions Summary

| Action | Doctor | Patient | Receptionist |
|--------|--------|---------|--------------|
| Register | ✅ | ✅ | ❌ (admin only) |
| Own profile | ✅ | ✅ | — |
| View appointments | Own only | Own only | All |
| Book appointment | ✅ | ✅ | ✅ |
| Change status | ✅ | ❌ | ✅ |

## Running Tests

```bash
python manage.py test
```