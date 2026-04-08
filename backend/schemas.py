from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- User schemas ----------


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=4, max_length=100)


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Auth / Token schemas ----------


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ---------- Task schemas ----------


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    importance: int = Field(ge=1, le=5, default=3)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    importance: Optional[int] = Field(default=None, ge=1, le=5)


class TaskRead(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PrioritizedTask(TaskRead):
    priority_score: float


class PrioritizedTaskList(BaseModel):
    tasks: List[PrioritizedTask]

