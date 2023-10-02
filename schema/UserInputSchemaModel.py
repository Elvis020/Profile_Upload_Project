import json
from typing import Optional, Type
import inspect

from fastapi import Form
from pydantic import BaseModel, EmailStr


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
            annotation=field.outer_type_,
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


@as_form
class UserInputModel(BaseModel):
    name: str
    email: EmailStr

    # @classmethod
    # def __get_validators__(cls):
    #     yield cls.validate_to_json
    #
    # @classmethod
    # def validate_to_json(cls, value):
    #     if isinstance(value, str):
    #         return cls(**json.loads(value))
    #     return value
    #
    class Config:
        orm_mode = True


class UserModel(BaseModel):
    name: str
    email: EmailStr
    profile_image_url: Optional[str]

    class Config:
        orm_mode = True
