from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, tasks, schedules, reminders


# FastAPI instance
app = FastAPI(
    title="Personal Assistant API",
    description="An API for users, tasks, schedules and reminders",
    version="1.0.0"
)

# CORS middleware (required for frontend or cross-origin access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change to specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes  
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(schedules.router)
app.include_router(reminders.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to your Personal Assistant API"}

  