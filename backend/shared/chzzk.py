import json
import logging
import urllib.request
from typing import TypedDict


class ChzzkChannel(TypedDict):
    channelId: str
    channelName: str
    channelImageUrl: str
    verifiedMark: bool


class ChzzkLive(TypedDict):
    liveId: int
    liveTitle: str
    status: str
    liveImageUrl: str
    defaultThumbnailImageUrl: str | None
    concurrentUserCount: int
    accumulateCount: int
    chatDonationRankingExposure: bool | None
    openDate: str
    closeDate: str
    adult: bool | None
    chatChannelId: str | None
    categoryType: str
    liveCategory: str
    liveCategoryValue: str
    chatActive: bool
    chatAvailableGroup: str
    paidPromotion: bool
    chatAvailableCondition: str
    minFollowerMinute: int
    livePlaybackJson: str
    channel: ChzzkChannel
    livePollingStatusJson: str
    userAdultStatus: str | None

    def __str__(self) -> str:
        return f"ChzzkLive(liveId={self.liveId}, liveTitle={self.liveTitle}, status={self.status})"

    def __repr__(self) -> str:
        return self.__str__()


class Streamer(TypedDict):
    openLive: bool


class Following(TypedDict):
    channel: ChzzkChannel
    liveInfo: ChzzkLive
    streamer: Streamer


def get_live_detail(chzzk_id: str, *, logger: logging.Logger | None = None) -> ChzzkLive | None:
    url = f"https://api.chzzk.naver.com/service/v2/channels/{chzzk_id}/live-detail"

    request = urllib.request.Request(url, method='GET')
    request.add_header('Content-Type', 'application/json')
    request.add_header('Origin', 'https://chzzk.naver.com')

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode('utf-8'))

    if data['code'] != 200:
        if logger is not None:
            logger.error({
                'type': 'CHZZK_LIVE_DETAIL_ERROR',
                'response': data
            })
        return None

    return data['content']


class ChatChannelAccessTokenTemporaryRestrict(TypedDict):
    temporaryRestrict: bool
    times: int
    duration: int | None
    createdTime: int | None


class ChatChannelAccessToken(TypedDict):
    accessToken: str
    temporaryRestrict: ChatChannelAccessTokenTemporaryRestrict
    realNameAuth: bool
    extraToken: str


def get_chat_channel_access_token(chat_channel_id: str, *, logger: logging.Logger | None = None) -> ChatChannelAccessToken | None:
    url = f"https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={chat_channel_id}&chatType=STREAMING"

    request = urllib.request.Request(url, method='GET')
    request.add_header('Content-Type', 'application/json')
    request.add_header('Origin', 'https://chzzk.naver.com')

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode('utf-8'))

    if data['code'] != 200:
        if logger is not None:
            logger.error({
                'type': 'CHAT_CHANNEL_ACCESS_TOKEN_ERROR',
                'response': data
            })
        return None

    return data['content']
