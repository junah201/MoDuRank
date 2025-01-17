import json
import uuid

import boto3
from pydantic import BaseModel, Field, ValidationError

from shared import (
    get_chat_channel_access_token,
    get_live_detail,
    get_logger,
    middleware,
)

dynamodb = boto3.client('dynamodb')

logger = get_logger()


class InitRoomParams(BaseModel):
    chzzk_id: str = Field(min_length=32, max_length=32, alias='chzzk_id')
    game_id: uuid.UUID = Field(alias='game_id')


@middleware(logger=logger)
def handler(event, _context):
    try:
        params = InitRoomParams.model_validate_json(event['body'])
    except ValidationError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e), ensure_ascii=False),
        }

    live_detail = get_live_detail(params.chzzk_id, logger=logger)

    if live_detail is None:
        return {
            'statusCode': 404,
            'body': {
                'detail': '해당 치지직 채널 정보를 찾을 수 없습니다.',
            }
        }

    chat_channel_id = live_detail['chatChannelId']
    chat_channel_access_token = get_chat_channel_access_token(
        chat_channel_id, logger=logger)

    if chat_channel_access_token is None:
        return {
            'statusCode': 500,
            'body': {
                'detail': '채팅 채널 접근 토큰을 가져올 수 없습니다.',
            }
        }

    # TODO: dynamoDB에 게임 정보 저장

    return {
        'statusCode': 200,
        'body': {
            'chat_channel_access_token': chat_channel_access_token,
            'live_detail': live_detail,
        }
    }
