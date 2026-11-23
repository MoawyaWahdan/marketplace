from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
    UploadFile,
    Query,
)

import logging


from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func, select, delete
from typing import Annotated

from app.db.database import get_session

from app.api.deps import UserDep, SessionDep
from app.utils.utils import upload_image_to_s3, get_image_url, delete_image_from_s3
