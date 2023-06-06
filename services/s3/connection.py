import io
import logging as logger
import os
from uuid import uuid4

import boto3
import magic
from botocore.exceptions import ClientError
from fastapi import UploadFile
from starlette import status

from services.s3.utils import check_file_greater_then_2MB, check_file_type_supported, SUPPORTED_FILE_TYPES

AWS_BUCKET = 'usersupload01'
s3 = boto3.resource('s3', aws_access_key_id=os.getenv('ACCESS_KEY'),
                    aws_secret_access_key=os.getenv('SECRET_KEY'))
bucket = s3.Bucket(AWS_BUCKET)


def s3_upload(contents: bytes, key: str):
    try:
        logger.info(f"Uploading {key} to s3")
        fo = io.BytesIO(contents)
        s3.meta.client.upload_fileobj(fo, AWS_BUCKET, key)
        return 'Success'
    except ClientError as e:
        logger.error(e)


def delete_image_from_s3(key: str) -> int:
    # Check if image is available before deletion
    all_files = list(map(lambda file: file.key, bucket.objects.all()))
    if key in all_files:
        s3.meta.client.delete_object(Bucket=AWS_BUCKET, Key=key)
        print('Successfully deleted image from s3')
        return status.HTTP_200_OK
    raise status.HTTP_404_NOT_FOUND


async def upload_image_to_s3(file: UploadFile):
    contents = await file.read()
    file_size = len(contents)
    file_type = magic.from_buffer(buffer=contents, mime=True)

    await check_file_greater_then_2MB(file_size)
    await check_file_type_supported(file_type)

    uploaded_file_name = file.filename.split('.')[0]
    file_name_to_s3 = f"{uploaded_file_name}-{str(uuid4()).split('-')[0]}.{SUPPORTED_FILE_TYPES[file_type]}"

    return f"https://s3.amazonaws.com/{AWS_BUCKET}/{file_name_to_s3}", contents, file_name_to_s3, uploaded_file_name
