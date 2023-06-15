from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: str
    date: datetime | None = None
    completed: bool = False
    image: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str | None] = None
    date: Optional[datetime]
    completed: Optional[bool] = False


class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True  # data["id"] or data.id va a ser leído correctamente


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    repeat_password: str


class User(UserBase):
    id: int
    tasks: list[Task] = []

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str

