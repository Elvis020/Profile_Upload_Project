from sqlalchemy import ForeignKey, Integer, Column, String
from sqlalchemy.orm import relationship

from db import Base


class ProfileImageModel(Base):
    __tablename__ = 'profile_image'
    id = Column(Integer, primary_key=True, index=True)
    upload_url = Column(String)
    # user_id = Column(Integer, ForeignKey("users.id"))
    #
    # user = relationship("UserModel", back_populates="profile_image")