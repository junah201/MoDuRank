import os

import boto3
from pydantic import BaseModel

from shared import get_logger, middleware
from shared.authorizer import login_required

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))

logger = get_logger()


class UserPublic(BaseModel):
    id: str
    email: str
    nickname: str
    permission: int


@middleware("GET", "/users/me", logger=logger, authorizer=login_required, tags=["users"])
def handler(event, _context):
    user = event["requestContext"]["user"]

    user_obj = UserPublic.model_validate(user)

    return {
        "statusCode": 200,
        "body": user_obj.dict(),
    }
