import os
from typing import Annotated

import boto3
from pydantic import BaseModel, Field

from shared import Permission, authorizer, get_logger, has_permission, middleware
from shared.parser.components import PathParams

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))

logger = get_logger()


class GetUserByIdPathParams(BaseModel):
    user_id: str = Field(min_length=32, max_length=32)


class UserPublic(BaseModel):
    user_id: str
    email: str
    nickname: str
    permission: int


@middleware(logger=logger)
@authorizer(
    logger=logger,
    permission=lambda permission: has_permission(permission, Permission.ADMIN),
)
def handler(_event, _context, path_params: Annotated[GetUserByIdPathParams, PathParams]):
    response = table.get_item(
        Key={
            "PK": f"USER#{path_params.user_id}",
            "SK": f"USER#{path_params.user_id}",
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

    return {
        "statusCode": 200,
        "body": user_obj.dict(),
    }
