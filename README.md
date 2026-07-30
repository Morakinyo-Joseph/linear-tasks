# Linear Tasks

Multi-tenant **Todo API** (Django + DRF + JWT). Backend only — no frontend.

Phase 2 wires the [Insider Python SDK](https://github.com/Insider-Inc/insider-python) so real exceptions beam into your Insider (StarLink) project for incidence / GitHub blame demos.

## Setup

```bash
cd "/home/candace/Documents/INSIDER TEST PROJECTS/linear-tasks"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8001
```

Use port **8001** if Insider itself is already on `8000`.

Health: [http://127.0.0.1:8001/health/](http://127.0.0.1:8001/health/)

## Auth

### Signup

```bash
curl -s -X POST http://127.0.0.1:8001/api/v1/auth/signup/ \
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
curl -s -X POST http://127.0.0.1:8001/api/v1/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email": "ada@linear.test", "password": "secret12345"}'
```

### Me

```bash
curl -s http://127.0.0.1:8001/api/v1/auth/me/ \
  -H "Authorization: Bearer $ACCESS"
```

## Todos

All todos are scoped to the caller’s organization.

```bash
# Create (priority: low|medium|high)
curl -s -X POST http://127.0.0.1:8001/api/v1/todos/ \
  -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"title": "Ship Phase 1", "description": "Auth + CRUD", "priority": "high"}'

# List (optional ?status=open|done&priority=high&q=ship)
curl -s 'http://127.0.0.1:8001/api/v1/todos/?priority=high' \
  -H "Authorization: Bearer $ACCESS"

# Complete
curl -s -X POST "http://127.0.0.1:8001/api/v1/todos/$TODO_ID/complete/" \
  -H "Authorization: Bearer $ACCESS"
```

## Tests

```bash
python manage.py test
```

## Phase 2 — Insider + StarLink

### 1. Install SDK

`requirements.txt` installs the local Insider monorepo SDK editable:

```text
-e "/home/candace/Documents/django-insider/project insider/sdk/python"
```

Init lives in `linear_tasks/wsgi.py` and `asgi.py` (before `get_*_application()`). No middleware and no `INSTALLED_APPS` entry.

### 2. Connect GitHub on the Insider project

In Insider (e.g. SpaceX / StarLink):

1. Create or open the project that will receive beams.
2. Connect GitHub repo **`Morakinyo-Joseph/linear-tasks`** (PAT or OAuth).
3. Copy the project **DSN** into Linear Tasks `.env`:

```bash
INSIDER_DSN=https://<beacon_token>@localhost:8000/<project_uuid>
INSIDER_ENVIRONMENT=development
INSIDER_DEBUG=true
```

Leave `INSIDER_RELEASE` and `GIT_SHA` **unset** on this machine. The SDK sets `release` from `git rev-parse HEAD` automatically. Do not paste commit SHAs into app code.

### 3. Beam a real error

With Insider running on `:8000` and Linear Tasks on `:8001`:

```bash
# Unhandled exception → request footprint (DEBUG only)
curl -s -i http://127.0.0.1:8001/api/v1/demo/boom/

# Manual notice (no raise)
curl -s http://127.0.0.1:8001/api/v1/demo/notice/
```

### 4. Incidence → GitHub blame recipe

1. Confirm the footprint appears under the Insider project.
2. Open / wait for the related **incidence**.
3. Suspect-commit / blame should resolve against **`Morakinyo-Joseph/linear-tasks`** history, using the footprint `release` / stack frames — not a hardcoded SHA in this repo.
4. Compare authors/releases across commits (initial vs later feature commits).

Demo routes (`/api/v1/demo/*`) return 404 when `DEBUG=False`.

### 5. Intentional schema-drift bug (migration `0002`)

Feature commit adds todo **`priority`**, but migration `0002_todo_priority_schema_drift` also **drops the `description` DB column** while the Django model/serializer still declare `description`.

After `migrate`, todo create/list raises `OperationalError` (no such column). That error beams into StarLink for blame against the commit that introduced the migration — useful for comparing `release` / git authors.
