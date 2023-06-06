from fastapi import UploadFile, File

from models.User import User
from schema.UserInputSchemaModel import UserInputModel
from services.s3.connection import upload_image_to_s3, s3_upload


async def create_user_object(user: UserInputModel, image: UploadFile = File(None)) -> User:
    if image is None:
        return User(name=user.name, email=user.email)
    else:
        profile_image_url, contents, file_name_to_s3, file_name = await upload_image_to_s3(image)
        result = s3_upload(contents=contents, key=file_name_to_s3)
        if result != 'Success':
            return None
        return User(name=user.name, email=user.email, profile_image_url=profile_image_url)
