import inspect
import json
import logging
import traceback

from pydantic import BaseModel, ValidationError

from shared.json import JsonEncoder
from shared.parser import Body, Component, Parameter, PathParams, get_args, is_annotated


def middleware(*, logger: logging.Logger):
    def outer(func):
        def inner(event, _context):
            logger.info(
                {
                    "type": "REQUEST",
                    "event": event,
                }
            )

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
                print(f"{base_type=}, {type(base_type)=}")

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
