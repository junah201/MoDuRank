import inspect
import json
import logging
import os
import traceback
from collections.abc import Callable
from decimal import Decimal
from functools import wraps
from typing import Annotated, Literal
from typing_extensions import Doc

import boto3
import jwt
from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo

from shared.json import JsonEncoder
from shared.parser import get_args, is_annotated
from shared.parser.params import Body, Path, Query
from shared.security import verify_access_token

a = FieldInfo(min_length=32, max_length=32, alias="chzzk_id")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))


def response_jsonify():
    def outer(func):
        @wraps(func)
        def inner(event, _context):
            res = func(event, _context)

            res = res or {}
            res["headers"] = res.get("headers", {})
            res["headers"]["Access-Control-Allow-Origin"] = "*"
            res["headers"]["Content-Type"] = "application/json"

            if isinstance(res.get("body", ""), dict):
                res["body"] = json.dumps(res["body"], ensure_ascii=False, cls=JsonEncoder)

            return res

        return inner

    return outer


def error_handler(logger: logging.Logger):
    def outer(func):
        @wraps(func)
        def inner(event, _context):
            try:
                return func(event, _context)
            except Exception as e:
                logger.error(
                    {"type": "UNHANDLED_ERROR", "error": str(e), "traceback": traceback.format_exc().splitlines()}
                )

                return {
                    "statusCode": 500,
                    "body": {
                        "detail": e,
                    },
                }

        return inner

    return outer


def log_request_and_response(logger: logging.Logger):
    def outer(func):
        @wraps(func)
        def inner(event, _context):
            # Log request
            logger.info(
                {
                    "type": "REQUEST",
                    "event": event,
                }
            )

            res = func(event, _context)

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

            if isinstance(res.get("body", ""), dict):
                res["body"] = json.dumps(res["body"], ensure_ascii=False, cls=JsonEncoder)

            return res

        return inner

    return outer


def authorize(logger: logging.Logger, authorizer: Callable[[int | Decimal], bool] | None = None):
    def outer(func):
        @wraps(func)
        def inner(event, _context):
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

            return func(event, _context)

        return inner

    return outer


def parser(
    logger: logging.Logger,
    original_func: Callable,
):
    def outer(func):
        @wraps(func)
        def inner(event, _context):
            signature = inspect.signature(original_func)

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

                if not issubclass(metadata, Path | Query | Body):
                    raise ValueError("Annotated type hint must be subclass of Path, Query or Body")

                if not issubclass(base_type, BaseModel | str | int):
                    raise ValueError("Annotated type hint must be subclass of BaseModel, str or int")

                if issubclass(metadata, Path):
                    source = event.get("pathParameters", "{}")
                elif issubclass(metadata, Query):
                    source = event.get("queryStringParameters", "{}")
                elif issubclass(metadata, Body):
                    source = event.get("body", "{}")
                else:
                    raise ValueError("Invalid metadata type. Must be one of Body, PathParams, Parameter")

                try:
                    if issubclass(base_type, str | int):
                        # TODO: Add validation for str and int
                        parsed_data[name] = base_type(source)
                except KeyError:
                    return {
                        "statusCode": 422,
                        "body": {
                            "detail": f"{name} is required.",
                        },
                    }
                except TypeError:
                    return {
                        "statusCode": 422,
                        "body": {
                            "detail": f"{name} must be {base_type.__name__}.",
                        },
                    }
                except ValueError:
                    return {
                        "statusCode": 422,
                        "body": {
                            "detail": f"{name} must be {base_type.__name__}.",
                        },
                    }

                try:
                    if issubclass(base_type, BaseModel):
                        parsed_data[name] = base_type.model_validate_json(source)
                except ValidationError as e:
                    return {
                        "statusCode": 422,
                        "body": {
                            "detail": str(e),
                        },
                    }

            return func(event, _context, **parsed_data)

        return inner

    return outer


def middleware(
    method: Literal["GET", "POST", "DELETE", "PUT", "OPTION", "PATCH"],
    path: str,
    *,
    logger: logging.Logger,
    tags: Annotated[list[str], Doc("The tags for swagger")] = [],
    authorizer: Callable[[int | Decimal], bool] | None = None,
):
    def decorator(func):
        func.method = method
        func.path = path
        func.tags = tags

        @response_jsonify()
        @log_request_and_response(logger)
        @error_handler(logger)
        @authorize(logger, authorizer)
        @parser(logger, original_func=func)
        @wraps(func)
        def wrapped(event, context, *args, **kwargs):
            return func(event, context, *args, **kwargs)

        return wrapped

    return decorator
