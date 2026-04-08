from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import ai, auth, tasks

# Create all database tables on startup (simple for small demo apps).
models.User.metadata.create_all(bind=engine)
models.Task.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Task Manager with AI Prioritization")

# In development we allow all origins to keep things simple.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(ai.router)


@app.get("/")
def read_root():
    return {"message": "Smart Task Manager API is running"}

