import os
from typing import Annotated

import boto3
from pydantic import BaseModel, EmailStr, Field

from shared import Body, create_access_token, get_logger, middleware, verify_password

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))

logger = get_logger()


class LoginBody(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=8, max_length=32)


@middleware(logger=logger)
def handler(_event, _context, body: Annotated[LoginBody, Body]):
    response = table.query(
        IndexName="GSI-email",
        KeyConditionExpression="email = :email AND begins_with(PK, :PK)",
        ExpressionAttributeValues={
            ":email": body.email,
            ":PK": "USER#",
        },
    )

    if not response.get("Items", []):
        return {
            "statusCode": 401,
            "body": {
                "detail": "이메일 또는 비밀번호가 일치하지 않습니다.",
            },
        }

    user = response["Items"][0]

    if not verify_password(body.password, user["password"]):  # type: ignore
        return {
            "statusCode": 401,
            "body": {
                "detail": "이메일 또는 비밀번호가 일치하지 않습니다.",
            },
        }

    token = create_access_token(
        {
            "sub": user["id"],
            "email": user["email"],
        }
    )

    return {
        "statusCode": 200,
        "body": {
            "detail": "로그인 성공",
            "token": token,
        },
    }
