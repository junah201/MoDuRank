import json
import logging
import traceback


def middleware(*, logger: logging.Logger):
    def outer(func):
        def inner(event, context):
            logger.info(
                json.dumps(
                    {
                        'type': 'REQUEST',
                        'event': event,
                    }
                )
            )

            try:
                res = func(event, context)
            except Exception as e:
                logger.error(
                    json.dumps(
                        {
                            'type': 'UNHANDLED_EXCEPTION',
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        },
                        ensure_ascii=False
                    )
                )
                res = {
                    'statusCode': 500,
                    'body': json.dumps(str(e), ensure_ascii=False),
                }

            res = res or {}
            body = res.get('body', '')
            if isinstance(body, dict):
                res['body'] = json.dumps(body, ensure_ascii=False)
            elif isinstance(body, str):
                res['body'] = body
            res['headers'] = res.get('headers', {})
            res['headers']['Access-Control-Allow-Origin'] = '*'
            res['headers']['Content-Type'] = 'application/json'

            logger.info(
                json.dumps(
                    {
                        'type': 'RESPONSE',
                        'response': res,
                    },
                    ensure_ascii=False
                )
            )

            return res

        return inner

    return outer
