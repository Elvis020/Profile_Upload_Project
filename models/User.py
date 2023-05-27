from sqlalchemy import ForeignKey, Integer, Column, String
from sqlalchemy.orm import relationship

from db import Base


# TODO: Do alembic revisions
class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    # profile_image_id = Column(Integer, ForeignKey("profile_image.id"))
    #
    # profile_image = relationship("ProfileImageModel", back_populates="user", uselist=False)