# Smart Task Manager with AI Prioritization

A full-stack task management app built with FastAPI and vanilla JavaScript.  
It supports user authentication, personal task CRUD, and AI-assisted task prioritization.

## Features

- User registration and login with JWT authentication
- Create, read, update, and delete personal tasks
- Task fields: title, description, deadline, importance
- AI prioritization endpoint to rank tasks by urgency/importance
- Heuristic fallback when ML model is disabled or unavailable
- Azure deployment workflows for backend and frontend

## Tech Stack

### Backend
- Python 3
- FastAPI
- SQLAlchemy
- JWT auth (`python-jose`)
- Password hashing (`passlib[bcrypt]`)
- Optional ML (`scikit-learn`, `joblib`)

### Frontend
- HTML, CSS, JavaScript (no frontend framework)
- Token-based API integration with `fetch`

## Project Structure

```text
taskmanager/
  backend/
    main.py
    config.py
    database.py
    models.py
    schemas.py
    auth_utils.py
    routers/
      auth.py
      tasks.py
      ai.py
    ml/
      README.md
      features.py
      inference.py
      train_model.py
      data/
        task_priority_training.csv
  frontend/
    index.html
    script.js
    style.css
    login.html
    register.html
    dashboard.html
    shared.js
    dashboard.js
    styles.css
  .github/workflows/
  requirements.txt
  .env.example
```

## API Overview

Base URL (local): `http://127.0.0.1:8000`

### Auth
- `POST /auth/register` - create user account
- `POST /auth/login` - login and receive bearer token

### Tasks (authenticated)
- `POST /tasks/` - create task
- `GET /tasks/` - list tasks for current user
- `GET /tasks/{task_id}` - get one task
- `PUT /tasks/{task_id}` - update task
- `DELETE /tasks/{task_id}` - delete task

### AI (authenticated)
- `GET /ai/prioritize` - return tasks sorted by priority score
- `GET /ai/model-status` - inspect ML status/debug info

## Local Setup

### 1) Clone and open project

```bash
git clone <your-repo-url>
cd taskmanager
```

### 2) Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Copy `.env.example` to `.env` and update values:

```powershell
Copy-Item .env.example .env
```

Minimum recommended values for local development:

- `DATABASE_URL=sqlite:///./smart_task_manager.db`
- `SECRET_KEY=<long-random-secret>`
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- `CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500`
- `USE_ML_PRIORITIZATION=false` (or `true` if model is prepared)

### 5) Run backend

```bash
uvicorn backend.main:app --reload
```

Open API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 6) Run frontend

Serve `frontend/` using a static server (for example VS Code Live Server), then open either:

- `frontend/index.html` (single-page style flow)
- or `frontend/login.html` (multi-page flow)

## AI Prioritization

The prioritization endpoint uses:

1. ML model inference when:
   - `USE_ML_PRIORITIZATION=true`, and
   - model file exists at `ML_MODEL_PATH`
2. Fallback heuristic when ML is disabled or model is unavailable

To train a model, see `backend/ml/README.md`.

## Deployment

The repository includes GitHub Actions workflows for:

- Azure App Service deployment (backend)
- Azure Static Web Apps deployment (frontend)

Set production secrets and environment variables in Azure and/or GitHub as required by your workflows.

## Notes and Current Limitations

- There are two frontend variants (`index.html` flow and `login/register/dashboard` flow).
- API base URL differs between frontend scripts (`script.js` uses deployed URL, `shared.js` uses localhost).
- Database migrations are not configured yet (tables are created at startup in `backend/main.py`).
- Automated tests are not set up yet.

## Recommended Next Improvements

- Add Alembic for schema migrations
- Add backend tests (pytest) for auth/tasks/ai routes
- Unify frontend into a single flow and centralize API base URL configuration
- Add CI checks (lint + tests) before deployment

## License

Add a `LICENSE` file if you plan to open-source or share this project publicly.
