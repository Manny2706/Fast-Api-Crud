from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskBase(BaseModel):
    title: constr(min_length=1, max_length=200)
    description: Optional[constr(max_length=1000)] = ""


class TaskCreate(TaskBase):
    pass


class TaskOut(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
