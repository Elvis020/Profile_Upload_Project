import json
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserInputModel(BaseModel):
    name: str
    email: EmailStr

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class UserModel(BaseModel):
    name: str
    email: EmailStr
    profile_image_url: Optional[str]

    class Config:
        orm_mode = True
