from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import CORS_ORIGINS
from .middleware.request_logging import RequestLoggingMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .observability import configure_application_insights, configure_logging
from .rate_limit import limiter
from .routers import admin, ai, auth, health, tasks
from .startup import init_database

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Smart Task Manager with AI Prioritization",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware order: last registered runs first on incoming requests.
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(ai.router)
app.include_router(admin.router)


@app.get("/")
def read_root():
    return {"message": "Smart Task Manager API is running"}


configure_application_insights(app)
