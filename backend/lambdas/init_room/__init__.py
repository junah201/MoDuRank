import uuid
from typing import Annotated

import boto3
from pydantic import BaseModel, Field

from shared import (
    Body,
    get_chat_channel_access_token,
    get_live_detail,
    get_logger,
    middleware,
)

dynamodb = boto3.client("dynamodb")

logger = get_logger()


class InitRoomBody(BaseModel):
    chzzk_id: str = Field(min_length=32, max_length=32, alias="chzzk_id")
    game_id: uuid.UUID = Field(alias="game_id")


@middleware(logger=logger)
def handler(_event, _context, body: Annotated[InitRoomBody, Body]):
    live_detail = get_live_detail(body.chzzk_id, logger=logger)

    if live_detail is None:
        return {
            "statusCode": 404,
            "body": {
                "detail": "해당 치지직 채널 정보를 찾을 수 없습니다.",
            },
        }

    chat_channel_id = live_detail["chatChannelId"]
    chat_channel_access_token = get_chat_channel_access_token(
        chat_channel_id, logger=logger
    )

    if chat_channel_access_token is None:
        return {
            "statusCode": 500,
            "body": {
                "detail": "채팅 채널 접근 토큰을 가져올 수 없습니다.",
            },
        }

    # TODO: dynamoDB에 게임 정보 저장

    return {
        "statusCode": 200,
        "body": {
            "chat_channel_access_token": chat_channel_access_token,
            "live_detail": live_detail,
        },
    }
