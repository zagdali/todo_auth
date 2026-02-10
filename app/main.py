# app\main.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.config.database import engine

from .auth import router as auth
from .routers import users, projects, lists, tasks, tags

import os

app = FastAPI(title="TODOLIST")

@app.on_event("startup") # Создаём таблицы после создания приложения
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(auth.router, prefix="/auth", tags=["auth"])
#app.include_router(users.router, prefix="/users", tags=["users"])
#app.include_router(projects.router, prefix="/projects", tags=["projects"])
#app.include_router(lists.router, prefix="/lists", tags=["lists"])
#app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
#app.include_router(tags.router, prefix="/tags", tags=["tags"])