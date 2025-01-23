import os
from typing import Annotated

import boto3
from pydantic import BaseModel, Field

from shared import get_logger, middleware
from shared.authorizer import admin_required
from shared.parser import Path

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))

logger = get_logger()


class GetUserByIdPathParams(BaseModel):
    user_id: str = Field(min_length=32, max_length=32)


class UserPublic(BaseModel):
    id: str
    email: str
    nickname: str
    permission: int


@middleware("GET", "/users/{user_id}", logger=logger, authorizer=admin_required, tags=["users"])
def handler(_event, _context, user_id: Annotated[str, Path()]):
    response = table.get_item(
        Key={
            "PK": f"USER#{user_id}",
            "SK": f"USER#{user_id}",
        },
    )

    if "Item" not in response:
        return {
            "statusCode": 404,
            "body": {
                "detail": "사용자를 찾을 수 없습니다.",
            },
        }

    user = response["Item"]

    user_obj = UserPublic.model_validate(user)
    user_data = user_obj.model_dump()

    return {
        "statusCode": 200,
        "body": user_data,
    }
