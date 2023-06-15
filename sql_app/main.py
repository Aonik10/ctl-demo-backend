from fastapi import Depends, FastAPI, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from typing import Annotated

from . import controllers, models, schemas, auth
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencias
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: Annotated[str, Depends(auth.oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = controllers.get_user_by_username(db, token_data.username)
    #user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Endpoints

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Me fijo si el usuario existe
    db_user = controllers.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    if user.password != user.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords must match!")
    # Si el usuario no existe, lo creo
    return controllers.create_user(db=db, user=user)


@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(current_user: Annotated[schemas.User, Depends(get_current_user)], filter: bool = None, db: Session = Depends(get_db)):
    tasks = controllers.get_tasks(db=db, user_id=current_user.id, filter=filter)
    return tasks


@app.post("/tasks/", response_model=schemas.Task)
def create_task(current_user: Annotated[schemas.User, Depends(get_current_user)], task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return controllers.create_task(db=db, task=task, user_id=current_user.id)


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, taskUpd: schemas.TaskUpdate, db: Session = Depends(get_db)):
    return controllers.update_task(db=db, task_id=task_id, taskUpd=taskUpd)


@app.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    return controllers.delete_task(db=db, task_id=task_id)


@app.post("/upload-image/")
async def upload_image(file: UploadFile):
    return await controllers.upload_image(file=file)


@app.get("/images/{image_name}")
async def get_image(image_name: str):
    return await controllers.get_image(image_name=image_name)

