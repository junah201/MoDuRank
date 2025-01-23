import os
import re
import uuid
from datetime import datetime, timezone
from typing import Annotated, Literal, Optional

import boto3
from pydantic import (
    BaseModel,
    Field,
    NonNegativeInt,
    PrivateAttr,
    computed_field,
    field_validator,
    model_validator,
)

from shared import Path, authorizer, get_logger, middleware

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))

logger = get_logger()


@middleware("PATCH", "/games/{game_id}/options", logger=logger, authorizer=authorizer.login_required, tags=["games"])
def handler(
    _event,
    _context,
    game_id: Annotated[
        str,
        Path(
            min_length=32,
            max_length=32,
            openapi_examples={
                "example 1": {"value": "a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5", "summary": "게임 ID"},
                "example 2": {"value": "a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5", "summary": "게임 ID"},
            },
        ),
    ],
):
    pass
