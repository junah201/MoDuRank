import os
import re
import uuid
from datetime import datetime, timezone
from typing import Annotated, Literal

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

from shared import Body, authorizer, get_logger, middleware

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "modurank-db"))

logger = get_logger()


class GameOption(BaseModel):
    type: Literal["Image", "Video"] = Field(description="이상형 후보 타입")
    title: str = Field(min_length=2, max_length=128)


class GameImageOption(GameOption):
    image_url: str = Field(min_length=0, max_length=1024, default="")


class GameYoutubeOption(GameOption):
    video_url: str = Field(min_length=0, max_length=1024, default="")
    start_time: NonNegativeInt | None = Field(default=None, description="시작 시간 (초)")
    end_time: int | None = Field(default=None, description="종료 시간 (초)")

    @field_validator("video_url")
    def validate_video_url(cls, video_url):
        video_url_regex = re.compile(
            r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})$"
        )
        if not video_url_regex.match(video_url):
            raise ValueError("유효한 Video URL이 아닙니다.")
        return video_url


class PostGameBody(BaseModel):
    _game_id: str = PrivateAttr(
        default_factory=lambda: uuid.uuid4().hex,
    )

    @computed_field(return_type=str)
    def game_id(self):
        return self._game_id

    title: str = Field(min_length=2, max_length=128)
    description: str = Field(min_length=0, max_length=1024, default="")
    tags: list[str] = Field(default_factory=list, description="게임 태그 목록")
    options: list[GameOption] = Field(default_factory=list, description="이상형 후보 목록")
    visibility: Literal["public", "private", "friends"] = Field(default="public", description="게임 공개 범위")
    password: str | None = Field(default=None, description="친구 공개 게임 비밀번호", min_length=4, max_length=32)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field(return_type=str)
    def PK(self):
        return f"GAME#{self.game_id}"

    @computed_field(return_type=str)
    def SK(self):
        return f"GAME#{self.game_id}"

    @model_validator(mode="after")
    def validate_visibility_and_password(cls, values):
        visibility = values.get("visibility")
        password = values.get("password")

        if visibility == "friends" and not password:
            raise ValueError("친구 공개 게임은 비밀번호가 필요합니다.")

        if visibility != "friends" and password:
            raise ValueError("친구 공개 게임이 아닌 경우 비밀번호를 설정할 수 없습니다.")

        return values


@middleware(logger=logger, authorizer=authorizer.login_required)
def handler(_event, _context, body: Annotated[PostGameBody, Body]):
    game_data = body.model_dump()
    game_data["user_id"] = _event["requestContext"]["user"]["id"]

    response = table.put_item(Item=game_data)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        logger.error(
            {
                "TYPE": "GAME_POST_FAIL",
                "response": response,
            }
        )

        return {
            "statusCode": 500,
            "body": {
                "detail": "게임 정보를 저장하는데 실패했습니다.",
            },
        }

    return {
        "statusCode": 200,
        "body": {
            "detail": "게임 정보를 성공적으로 등록했습니다.",
            "game_id": game_data["game_id"],
        },
    }
