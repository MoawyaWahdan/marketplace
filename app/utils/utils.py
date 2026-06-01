from fastapi import UploadFile
import uuid
import boto3
import os
from app.core.config import (
    S3_BUCKET_NAME,
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def upload_image_to_s3(file: UploadFile) -> str:
    extension = file.filename.split(".")[-1]

    object_key = f"listings/{uuid.uuid4()}.{extension}"

    s3_client.upload_fileobj(
        file.file,
        S3_BUCKET_NAME,
        object_key,
        ExtraArgs={"ContentType": file.content_type},
    )

    return object_key


def get_image_url(key: str) -> str:
    return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"


def delete_image_from_s3(object_key: str):
    s3_client.delete_object(
        Bucket=S3_BUCKET_NAME,
        Key=object_key,
    )
