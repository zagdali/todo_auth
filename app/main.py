from fastapi import FastAPI
from .routers import users, projects, lists, tasks, tags
from .database import engine
from .models import Base

import os

app = FastAPI(title="TODOLIST")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(lists.router, prefix="/lists", tags=["lists"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])