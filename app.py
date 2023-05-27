from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from db import Base, engine, SessionLocal
from models.User import UserModel
from schema.UserSchema import UserSchema

app = FastAPI()
Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/",
    description="Docs",
    tags=["Users"],
    response_class=RedirectResponse,
)
def home():
    return RedirectResponse("/docs")


@app.get("/users", tags=["Users"],status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()


@app.get("/users/{user_id}", tags=["Users"],status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'User with id {user_id} is not available')
    return user


@app.post("/users", tags=["Users"],status_code=status.HTTP_201_CREATED)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    new_user = UserModel(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.put("/users/{user_id}", tags=["Users"],status_code=status.HTTP_202_ACCEPTED)
def update_user(user_id: int, user: UserSchema, db: Session = Depends(get_db)):
    db.query(UserModel).filter(UserModel.id == user_id).update({
        'name': user.name,
        'email': user.email,
    })
    db.commit()
    return 'User details updated successfully'


@app.delete("/users/{user_id}", tags=["Users"],status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db.query(UserModel).filter(UserModel.id == user_id).delete(synchronize_session=False)
    db.commit()
    return 'Successfully deleted user'
