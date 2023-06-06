from fastapi import UploadFile, FastAPI, File
from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from db import Base, engine, SessionLocal
from models.User import User
from schema.UserInputSchemaModel import UserInputModel
from utils.utils import create_user_object

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


@app.get("/users", tags=["Users"], status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/{user_id}", tags=["Users"], status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'User with id {user_id} is not available')
    return user


@app.post("/users", tags=["Users"], status_code=status.HTTP_201_CREATED)
async def create_user(user: UserInputModel, image: UploadFile = File(None), db: Session = Depends(get_db)):
    new_user = await create_user_object(user, image)
    if new_user is not None:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    return status.HTTP_406_NOT_ACCEPTABLE


@app.put("/users/{user_id}", tags=["Users"], status_code=status.HTTP_202_ACCEPTED)
async def update_user(user_id: int, user: UserInputModel, image: UploadFile = File(None),
                      db: Session = Depends(get_db)):
    updated_user = await create_user_object(user, image)
    if updated_user is not None:
        db.query(User).filter(User.id == user_id).update({
            'name': updated_user.name,
            'email': updated_user.email,
            'profile_image_url': updated_user.profile_image_url
        })
        db.commit()
        return 'User details updated successfully'
    return status.HTTP_404_NOT_FOUND


@app.delete("/users/{user_id}", tags=["Users"], status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id)
    if not user.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'User with id {user_id} is not available')
    user.delete(synchronize_session=False)
    db.commit()
    return 'Successfully deleted user'
