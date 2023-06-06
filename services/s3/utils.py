from fastapi import HTTPException, status, File, UploadFile

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
}


async def check_file_greater_then_2MB(file_size):
    if not 0 < file_size <= 2 * MB:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Supported file size is 0 - 2 MB')


async def check_file_type_supported(file_type):
    if file_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Unsupported file type: {file_type}. Supported types are:{SUPPORTED_FILE_TYPES}")


