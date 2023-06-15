from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from pathlib import Path

from . import models, schemas, auth


def get_tasks(db: Session, user_id: int, filter: bool = None):
    print(user_id)
    if filter is not None:
        db_tasks = db.query(models.Task).filter_by(completed=filter, owner_id=user_id).all()
    else:
        db_tasks = db.query(models.Task).filter_by(owner_id=user_id).all()
    return db_tasks


def create_task(db: Session, user_id, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, taskUpd: schemas.TaskUpdate):
    db_task = db.query(models.Task).get(task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in taskUpd.dict().items():
        if value is not None:
            setattr(db_task, key, value)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).get(task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return db_task


async def upload_image(file: UploadFile):
    current_dir = Path.cwd()
    images_dir = current_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    image_name = f"{uuid4()}{os.path.splitext(file.filename)[-1]}"

    file_path = images_dir / image_name
    with file_path.open("wb") as buffer:
        buffer.write(await file.read())

    return {"image": image_name}


async def get_image(image_name: str):
    current_dir = Path.cwd()
    images_dir = current_dir / "images"
    file_path = images_dir / image_name

    if file_path.is_file():
        return FileResponse(file_path)

    return FileResponse(images_dir / "no-image.jpg")


#####  ACA NUEVO  ####


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserBase):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
