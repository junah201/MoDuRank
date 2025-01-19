import os
import uuid

import boto3
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    PrivateAttr,
    ValidationError,
    computed_field,
)

from shared import get_logger, get_password_hash, middleware

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))

logger = get_logger()


class RegisterUserBody(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=8, max_length=32)
    nickname: str = Field(min_length=2, max_length=32)

    _user_id: str = PrivateAttr(
        default_factory=lambda: uuid.uuid4().hex,
    )

    _permission: int = PrivateAttr(default=1)

    @computed_field(return_type=str)
    def user_id(self):
        return self._user_id

    @computed_field(return_type=int)
    def permission(self):
        return self._permission

    @computed_field(return_type=str)
    def PK(self):
        return f"USER#{self.user_id}"

    @computed_field(return_type=str)
    def SK(self):
        return f"USER#{self.user_id}"


@middleware(logger=logger)
def handler(event, _context):
    try:
        body = RegisterUserBody.model_validate_json(event["body"])
    except ValidationError as e:
        return {
            "statusCode": 422,
            "body": {
                "detail": str(e),
            },
        }

    response = table.query(
        IndexName="GSI-email",
        KeyConditionExpression="email = :email AND begins_with(PK, :PK)",
        ExpressionAttributeValues={
            ":email": body.email,
            ":PK": "USER#",
        },
    )

    if "Items" in response and len(response["Items"]) > 0:
        return {
            "statusCode": 409,
            "body": {"detail": "해당 이메일로 가입된 계정이 이미 존재합니다."},
        }

    user_data = body.model_dump()
    user_data["password"] = get_password_hash(user_data["password"])

    response = table.put_item(Item=user_data)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        logger.error(
            {
                "TYPE": "USER_REGISTER_FAIL",
                "response": response,
            }
        )
        return {
            "statusCode": 500,
            "body": {
                "detail": "해당 유저를 등록하는 중 오류가 발생했습니다.",
            },
        }

    logger.info(
        {
            "TYPE": "USER_REGISTER_SUCCESS",
            "user_id": user_data["user_id"],
            "email": user_data["email"],
        }
    )
    return {
        "statusCode": 201,
        "body": {
            "detail": "유저 등록에 성공했습니다.",
        },
    }
