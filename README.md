# Linear Tasks

Multi-tenant **Todo API** (Django + DRF + JWT). Backend only — no frontend.

## Setup

```bash
cd "/home/candace/Documents/INSIDER TEST PROJECTS/linear-tasks"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Health: [http://127.0.0.1:8000/health/](http://127.0.0.1:8000/health/)

## Auth

### Signup

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/signup/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "ada@linear.test",
    "password": "secret12345",
    "first_name": "Ada",
    "last_name": "Lovelace",
    "organization_name": "Linear HQ"
  }'
```

Save `tokens.access` from the response.

### Login

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email": "ada@linear.test", "password": "secret12345"}'
```

### Me

```bash
curl -s http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer $ACCESS"
```

## Todos

All todos are scoped to the caller’s organization.

```bash
# Create
curl -s -X POST http://127.0.0.1:8000/api/v1/todos/ \
  -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"title": "Ship Phase 1", "description": "Auth + CRUD"}'

# List (optional ?status=open|done&q=ship)
curl -s 'http://127.0.0.1:8000/api/v1/todos/' \
  -H "Authorization: Bearer $ACCESS"

# Complete
curl -s -X POST "http://127.0.0.1:8000/api/v1/todos/$TODO_ID/complete/" \
  -H "Authorization: Bearer $ACCESS"
```

## Tests

```bash
python manage.py test
```

## Phase 2 (later)

Insider Python SDK + `INSIDER_DSN` middleware slot is reserved in settings for beaming real errors into StarLink.
