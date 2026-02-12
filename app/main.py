# app\main.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.config.database import engine

from .auth import router as auth
from .routers import users, projects, lists, tasks, tags
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="TODOLIST", lifespan=lifespan)




app.include_router(auth.router, prefix="/auth", tags=["auth"])
#app.include_router(users.router, prefix="/users", tags=["users"])
#app.include_router(projects.router, prefix="/projects", tags=["projects"])
#app.include_router(lists.router, prefix="/lists", tags=["lists"])
#app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
#app.include_router(tags.router, prefix="/tags", tags=["tags"])