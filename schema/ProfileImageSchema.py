from pydantic import BaseModel


class ProfileImageSchema(BaseModel):
    upload_image_url: str
    upload_image: str

    class Config:
        orm_mode = True