import logging
import os

import boto3
import jwt

from shared.security import verify_access_token

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))


def authorizer(*, logger: logging.Logger):
    def outer(func):
        def inner(event, context):
            token = event.get("headers", {}).get("authorization", None)

            if not token:
                return {
                    "statusCode": 401,
                    "body": {
                        "detail": "로그인이 필요합니다.",
                    },
                }

            try:
                payload = verify_access_token(token)
                user_id = payload["sub"]

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
                            "detail": "사용자 정보를 찾을 수 없습니다.",
                        },
                    }

                user = response["Item"]
                event["requestContext"] = event.get("requestContext", {})
                event["requestContext"]["user"] = user

                logger.info(
                    {
                        "type": "AUTHORIZER",
                        "user_id": user["user_id"],
                        "email": user["email"],
                    }
                )

                return func(event, context)
            except jwt.ExpiredSignatureError:
                return {
                    "statusCode": 401,
                    "body": {
                        "detail": "토큰이 만료되었습니다.",
                    },
                }
            except jwt.InvalidTokenError:
                return {
                    "statusCode": 401,
                    "body": {
                        "detail": "토큰이 유효하지 않습니다.",
                    },
                }

        return inner

    return outer
