# Smart Task Manager with AI Prioritization

Full-stack task manager with FastAPI, vanilla JavaScript, optional ML prioritization, Docker packaging, Azure-friendly configuration, Application Insights hooks, rate limiting, JWT refresh tokens, and lightweight RBAC.

## Capabilities

- JWT authentication (`POST /auth/register`, `POST /auth/login`) with bcrypt password hashing  
- **Refresh tokens**: `POST /auth/refresh` returns rotated refresh JWTs (`jti` ensures uniqueness)  
- **RBAC**: users listed in `ADMIN_EMAILS` receive role `admin`; `GET /admin/ping` is admin-only  
- Task CRUD scoped per user (`/tasks`)  
- AI prioritization (`GET /ai/prioritize`) with ML or heuristic fallback  
- **Ops**: `GET /health` (DB probe), structured request logging middleware, security headers, SlowAPI rate limits  
- **Azure Monitor**: optional OpenTelemetry export when `APPLICATIONINSIGHTS_CONNECTION_STRING` is set  
- **Docker Compose**: API + PostgreSQL + nginx frontend  
- **Terraform**: sample Azure RG + PostgreSQL Flexible Server + Log Analytics + Application Insights + Linux Web App  
- **CI/CD**: GitHub Actions run `pytest`; Azure Web App workflow runs tests before deploy; Docker image build workflow  

## Repository layout (high level)

```text
taskmanager/
  .dockerignore             # Shrinks image build context (repo root)
  docker-compose.yml
  backend/
    Dockerfile
    .dockerignore
    main.py                 # FastAPI app wiring, middleware, lifespan
    config.py               # Environment-driven settings
    database.py
    models.py               # User.role added (non-breaking via startup ALTER when needed)
    schemas.py              # Token includes optional refresh_token
    auth_utils.py           # Access + refresh JWT helpers, RBAC dependency
    db_schema.py            # Adds users.role on legacy databases
    rate_limit.py           # SlowAPI limiter
    observability.py        # Application Insights / logging bootstrap
    middleware/
      request_logging.py
      security_headers.py
    routers/
      auth.py               # register/login/refresh + limits
      tasks.py
      ai.py
      health.py             # GET /health
      admin.py              # Admin-only sample route
    ml/
  frontend/
    Dockerfile
    .dockerignore
    nginx.conf              # Used by frontend container
    ...
  infra/terraform/
    main.tf
    variables.tf
    outputs.tf
    terraform.tfvars.example
  tests/
  docker-compose.yml
  requirements.txt
  .env.example
  pytest.ini
  .github/workflows/
```

## API quick reference

Base URL (local): `http://127.0.0.1:8000`

| Area | Endpoint | Notes |
|------|----------|-------|
| Health | `GET /health` | Returns `{status, database}` |
| Auth | `POST /auth/register` | JSON `{email,password}`; assigns `admin` if email ∈ `ADMIN_EMAILS` |
| Auth | `POST /auth/login` | OAuth2 password form (`username`=email); returns `access_token` + `refresh_token` |
| Auth | `POST /auth/refresh` | JSON `{refresh_token}`; rotates refresh token |
| Tasks | `/tasks/...` | Bearer access token required |
| AI | `/ai/...` | Bearer access token required |
| Admin | `GET /admin/ping` | Bearer token + `admin` role |

Interactive docs: `/docs`, `/redoc`.

### Backward compatibility

- Existing clients that only read `access_token` continue to work; `refresh_token` is additional JSON.  
- Older access tokens without a `typ` claim still validate (`typ` may be `access` or omitted).  
- New deployments automatically create `users.role`; existing SQLite/PostgreSQL databases gain the column via startup patch (`db_schema.ensure_users_role_column`).  

## Local development (without Docker)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # then edit values
uvicorn backend.main:app --reload
```

Serve `frontend/` with any static server (VS Code Live Server, `python -m http.server`, etc.).

Run tests:

```powershell
python -m pytest -q
```

## Docker & Compose

Build/run everything (API + PostgreSQL + nginx):

```powershell
docker compose up --build
```

- API: `http://localhost:8000` (`GET /health`, `/docs`)  
- Frontend container: `http://localhost:8080` (proxies static files; API URL in JS may still point to Azure unless you change `frontend/script.js` / `shared.js`)  

Environment variables for Compose are documented inline in `docker-compose.yml` (override via shell or `.env` next to the compose file).

### Production-oriented container notes

- Backend image runs Gunicorn + Uvicorn workers.  
- Provide strong `SECRET_KEY` / `REFRESH_SECRET_KEY`, PostgreSQL credentials, and Azure connection strings via orchestrator secrets—not compose defaults.  
- Mount ML artifacts if `USE_ML_PRIORITIZATION=true`.  

## Azure deployment integration

### Application Insights / Azure Monitor

1. Create or reuse an Application Insights resource (workspace-backed).  
2. Copy the **connection string** into App Service settings as `APPLICATIONINSIGHTS_CONNECTION_STRING`.  
3. Redeploy/restart the API; telemetry flows via OpenTelemetry exporters (`azure-monitor-opentelemetry` + FastAPI instrumentation).  
4. Without the connection string the app logs only to stdout/stderr (ideal for container/App Service log streams).  

Additional logging:

- `smart_task_manager.request` logger emits method/path host + duration for each request.  
- Azure diagnostics can ingest stdout/stderr alongside traces/metrics from Insights.  

### GitHub Actions

- `/.github/workflows/ci.yml` — runs `pytest` on pushes/PRs.  
- `/.github/workflows/main_taskmanager-api-123.yml` — builds artifact and deploys to Azure Web App `taskmanager-api-123` (includes pytest gate before packaging).  
- `/.github/workflows/docker-build.yml` — validates Dockerfiles (`push` to `main` or manual dispatch).  
- Existing Static Web Apps workflow continues to publish `frontend/`.  

### Recommended App Service settings (conceptual)

Mirror `.env.example` keys (`DATABASE_URL`, `SECRET_KEY`, `REFRESH_SECRET_KEY`, `CORS_ORIGINS`, `ADMIN_EMAILS`, rate limits, ML toggles, Insights connection string). Prefer **Key Vault references** instead of storing passwords directly in app settings when possible.

### Aligning with existing Azure resources

If you already provisioned resources such as `CLOUD_PROJECT`, `taskmanager-api-123`, `taskmanagerpg123`, and `taskmanageracr1`:

- Point `DATABASE_URL` at `taskmanagerpg123` (encoded credentials).  
- Continue deploying the Web App via your existing workflow or push containers to `taskmanageracr1` (requires swapping the Web App to a container image—outside this repo’s defaults).  
- Terraform below can provision **parallel** infrastructure or serve as a reference; import/adjust modules rather than duplicating production names blindly.  

## Terraform add-ons (Insights, Key Vault, Storage — existing resource group)

If you already use **`CLOUD_PROJECT`** and **`taskmanager-api-123`**, use this stack to create **only** Log Analytics, Application Insights, Key Vault, and a Storage Account in that resource group.

**Full walkthrough (login, `tfvars`, `init` / `plan` / `apply`, App Service wiring, Key Vault next steps):**  
[`infra/terraform/azure-taskmanager-addons/README.md`](infra/terraform/azure-taskmanager-addons/README.md)

Quick copy-paste:

```powershell
cd infra/terraform/azure-taskmanager-addons
az login
Copy-Item terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — unique key_vault_name and storage_account_name
terraform init
terraform plan
terraform apply
terraform output -raw application_insights_connection_string
```

Set **`APPLICATIONINSIGHTS_CONNECTION_STRING`** on **`taskmanager-api-123`** to that value, then restart the Web App.

## Terraform (Azure sample stack)

Files live in `infra/terraform/` (greenfield template: RG + PostgreSQL + Web App + monitoring).

```powershell
cd infra/terraform
copy terraform.tfvars.example terraform.tfvars   # edit values; never commit secrets
terraform init
terraform plan
terraform apply
```

Creates:

- Resource group  
- PostgreSQL Flexible Server + DB + Azure-services firewall rule  
- Log Analytics workspace + Application Insights  
- Linux App Service Plan + Linux Web App with `/health` probe & startup command  

Outputs include web hostname and sensitive Insight connection material.

**Security note:** the template sets `DATABASE_URL` directly for demonstration ease. For production, prefer secrets stored in Key Vault with `@Microsoft.KeyVault(...)` references.

## Security features summary

| Feature | Implementation |
|---------|----------------|
| Password hashing | bcrypt via Passlib |
| Access JWT | HS256, configurable TTL |
| Refresh JWT | Separate signing secret (`REFRESH_SECRET_KEY`), rotated via `/auth/refresh`, carries unique `jti` |
| RBAC | `users.role` (`user` / `admin`), enforced via `require_roles` dependency |
| Rate limiting | SlowAPI defaults + tighter limits on `/auth/*` |
| HTTP headers | `SecurityHeadersMiddleware` adds baseline secure headers |
| Telemetry | Optional export to Application Insights |

## Troubleshooting

- **CORS errors**: ensure browser origin appears exactly in `CORS_ORIGINS`. Docker adds port `8080` examples to `.env.example`.  
- **Insights not reporting**: verify connection string, restart App Service, check quotas/network egress.  
- **SlowAPI + sync routes**: rate-limit header injection is disabled (`headers_enabled=False`) for compatibility with FastAPI dict responses.  
- **PostgreSQL passwords with symbols**: URL-encode credentials inside `DATABASE_URL`.  

## License

Add a `LICENSE` file if you distribute the project publicly.
