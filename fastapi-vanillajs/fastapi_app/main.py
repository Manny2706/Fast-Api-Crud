from fastapi import FastAPI, Depends, HTTPException, status
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, models, schemas, auth
from .database import engine, init_db, SessionLocal

load_dotenv()
app = FastAPI(title="FastAPI VanillaJS Demo")
# allow all origins for simplicity, in production you should specify allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()



@app.post("/api/v1/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    if crud.get_user_by_username(db, user_in.username) or crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="User with that username or email already exists")
    user = crud.create_user(db, user_in)
    return user


@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/users/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.get("/api/v1/users", response_model=list[schemas.UserOut])
def list_users(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(auth.get_db)):
    return db.query(models.User).all()


@app.post("/api/v1/users/{user_id}/promote")
def promote_user(user_id: int, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = "admin"
    db.commit()
    db.refresh(user)
    return {"success": True, "user": schemas.UserOut.from_orm(user)}


@app.post("/api/v1/tasks", response_model=schemas.TaskOut)
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_task(db, owner_id=current_user.id, task=task_in)


@app.get("/api/v1/tasks", response_model=list[schemas.TaskOut])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(auth.get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit)


@app.get("/api/v1/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(auth.get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/api/v1/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task_in: schemas.TaskCreate, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    updated = crud.update_task(db, task_id, task_in)
    return updated


@app.delete("/api/v1/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    ok = crud.delete_task(db, task_id)
    return {"success": ok}
