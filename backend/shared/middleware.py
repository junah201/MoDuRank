import json
import logging
import traceback


def middleware(*, logger: logging.Logger):
    def outer(func):
        def inner(event, context):
            logger.info(
                {
                    "type": "REQUEST",
                    "event": event,
                }
            )

            try:
                res = func(event, context)
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
                    "body": json.dumps(str(e), ensure_ascii=False),
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
                res["body"] = json.dumps(body, ensure_ascii=False)
            elif isinstance(body, str):
                res["body"] = body

            return res

        return inner

    return outer
