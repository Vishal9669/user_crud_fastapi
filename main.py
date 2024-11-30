from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database configuration
DATABASE_URL = "mysql+pymysql://root:Vishal%4096695@localhost:3306/user_crud_fastapi"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model for the User table
class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    location = Column(String(50), nullable=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic models for validation
class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(None, gt=5, lt=130)
    location: Optional[str] = None

class UserUpdate(User):
    age: int = Field(None, gt=5, lt=200)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI()

# Helper functions
def ensure_username_in_db(db: Session, username: str):
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Username {username} not found",
        )
    return user

# Routes
@app.get("/users")
def get_users_query(limit: int = 20, db: Session = Depends(get_db)):
    users = db.query(UserModel).limit(limit).all()
    return users

@app.get("/users/{username}")
def get_users_path(username: str, db: Session = Depends(get_db)):
    user = ensure_username_in_db(db, username)
    return user

@app.post("/users")
def create_user(user: User, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot create user. Username {user.username} already exists.",
        )
    new_user = UserModel(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"Successfully created user: {user.username}"}

@app.put("/users")
def update_user(user: User, db: Session = Depends(get_db)):
    existing_user = ensure_username_in_db(db, user.username)
    for key, value in user.dict().items():
        setattr(existing_user, key, value)
    db.commit()
    return {"message": f"Successfully updated user: {user.username}"}

@app.patch("/users")
def update_user_partial(user: UserUpdate, db: Session = Depends(get_db)):
    existing_user = ensure_username_in_db(db, user.username)
    for key, value in user.dict(exclude_unset=True).items():
        setattr(existing_user, key, value)
    db.commit()
    return {"message": f"Successfully updated user: {user.username}"}

@app.delete("/users")
def delete_user(username: str, db: Session = Depends(get_db)):
    existing_user = ensure_username_in_db(db, username)
    db.delete(existing_user)
    db.commit()
    return {"message": f"Successfully deleted user: {username}"}
