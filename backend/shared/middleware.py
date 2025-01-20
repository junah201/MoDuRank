import inspect
import json
import logging
import os
import traceback
from collections.abc import Callable
from decimal import Decimal

import boto3
import jwt
from pydantic import BaseModel, ValidationError

from shared.json import JsonEncoder
from shared.parser import Body, Component, Parameter, PathParams, get_args, is_annotated
from shared.security import verify_access_token

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))


def middleware(*, logger: logging.Logger, authorizer: Callable[[int | Decimal], bool] | None = None):
    def outer(func):
        def inner(event, _context):
            # Log request
            logger.info(
                {
                    "type": "REQUEST",
                    "event": event,
                }
            )

            # Authorizer
            if authorizer:
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

                    if not authorizer(user.get("permission", 0)):  # type: ignore
                        return {
                            "statusCode": 403,
                            "body": {
                                "detail": "권한이 없습니다.",
                            },
                        }

                    event["requestContext"] = event.get("requestContext", {})
                    event["requestContext"]["user"] = user

                    logger.info(
                        {
                            "type": "AUTHORIZER",
                            "user_id": user["id"],
                            "email": user["email"],
                        }
                    )
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

            # Parse parameters
            signature = inspect.signature(func)

            if len(signature.parameters) < 2:
                raise ValueError("handler function must have at least 2 parameters for event, _context")

            parsed_data = {}
            for name, param in signature.parameters.items():
                if name in ["event", "_event", "context", "_context"]:
                    continue

                annotation = param.annotation

                if not is_annotated(annotation):
                    continue

                base_type, metadata, *_ = get_args(annotation)

                if not issubclass(metadata, Component):
                    raise ValueError("Annotated type hint must be subclass of Component")

                if not issubclass(base_type, BaseModel):
                    raise ValueError("Annotated type hint must be subclass of BaseModel")

                try:
                    if issubclass(metadata, Body):
                        parsed_data[name] = base_type.model_validate_json(event.get("body", "{}"))
                    elif issubclass(metadata, PathParams):
                        parsed_data[name] = base_type.model_validate_json(event.get("pathParameters", "{}"))
                    elif issubclass(metadata, Parameter):
                        parsed_data[name] = base_type.model_validate_json(event.get("queryStringParameters", "{}"))
                    else:
                        raise ValueError("Invalid metadata type. Must be one of Body, PathParams, Parameter")
                except ValidationError as e:
                    return {
                        "statusCode": 422,
                        "body": {
                            "detail": str(e),
                        },
                    }

            try:
                res = func(event, _context, **parsed_data)
            except Exception as e:
                logger.error(
                    {
                        "type": "UNHANDLED_EXCEPTION",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    },
                )
                res = {
                    "statusCode": 500,
                    "body": json.dumps(str(e), ensure_ascii=False, cls=JsonEncoder),
                }

            res = res or {}
            res["headers"] = res.get("headers", {})
            res["headers"]["Access-Control-Allow-Origin"] = "*"
            res["headers"]["Content-Type"] = "application/json"

            # Log response
            logger.info(
                {
                    "type": "RESPONSE",
                    "response": res,
                }
            )

            body = res.get("body", "")
            if isinstance(body, dict):
                res["body"] = json.dumps(body, ensure_ascii=False, cls=JsonEncoder)
            elif isinstance(body, str):
                res["body"] = body

            return res

        return inner

    return outer
