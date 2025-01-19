import uuid
from typing import Annotated

import boto3
from pydantic import BaseModel, Field

from shared import Body, get_logger, middleware

dynamodb = boto3.client("dynamodb")

logger = get_logger()


class PostGameBody(BaseModel):
    game_id: str = Field(
        min_length=32,
        max_length=32,
        default_factory=lambda: uuid.uuid4().hex,
    )


@middleware(logger=logger)
def handler(_event, _context, body: Annotated[PostGameBody, Body]):
    # TODO: dynamoDB에 게임 정보 저장
    dynamodb.put_item(
        TableName="Game",
        Item={
            "PK": {"S": f"GAME#{body.game_id}"},
            "SK": {"S": f"GAME#{body.game_id}"},
            "game_id": {"S": body.game_id},
        },
    )

    return {"statusCode": 200, "body": {}}
