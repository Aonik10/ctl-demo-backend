from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


class Task(BaseModel):
    title: str
    description: str
    date: datetime
    completed: bool = False
    image: str


Tasks = List[Task]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/tasks")
def get_tasks():
    return {"message": "all tasks"}


@app.get("/tasks/{id}")
def get_task_by_id(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/tasks")
def create_task(task: Task):
    return {"crear una tarea nueva"}


@app.put("/tasks/{id}")
def create_task(task: Task):
    return {"actualizar"}


@app.delete("/tasks/{id}")
def create_task(task: Task):
    return {"eliminar una tarea"}

