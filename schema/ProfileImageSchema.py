from pydantic import BaseModel


class ProfileImageSchema(BaseModel):
    upload_url: str
    user_id: int

    class Config:
        orm_mode = True