from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import IntEnum
from typing import Any


@dataclass
class RawMediaInfo:
    provider: str
    playback_info: PlaybackInfo
    timeline_properties: TimelineProperties
    media_properties: MediaProperties


@dataclass
class PlaybackInfo: ...


@dataclass
class TimelineProperties: ...


@dataclass
class MediaProperties:
    title: str
    artist: str

    album_title: str
    album_artist: str
    album_track_count: int

    track_number: int
    subtitle: str
    genres: list[str]

    # We can store thumbnail in different ways:
    # 1. WinRT StreamRef (original data)
    # 2. Base64
    # 3. File path       (needs saving => side effects)
    # 4. Raw
    thumbnail: str  # path
    thumbnail_data: str  # base64

    playback_type: str


class MediaRepeat(IntEnum):
    NONE = 0
    TRACK = 1
    LIST = 2


@dataclass(frozen=True)
class MediaInfo:
    title: str = ""
    artist: str = ""

    album_title: str = ""
    album_artist: str = ""

    album_track_count: int = 0
    track_number: int = 0

    genres: list[str] = []

    cover: str = ""  # filepath
    cover_data: str = ""  # base64 string

    position: int = 0  # microseconds
    duration: int = 0  # microseconds

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
