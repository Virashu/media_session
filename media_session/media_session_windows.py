"""
Media controller using WinRT.Windows.Media.Control

Time variables is stored primarily in microseconds
"""

__all__ = ["MediaSessionWindows", "MediaRepeatMode"]

import asyncio
import logging
from base64 import b64encode
from datetime import timedelta
from pprint import pformat
from time import time
from typing import Any, Optional, final

# isort: off

from winrt.windows.media import MediaPlaybackAutoRepeatMode as MediaRepeatMode
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSession as _MediaSession,
    GlobalSystemMediaTransportControlsSessionManager as _MediaManager,
    GlobalSystemMediaTransportControlsSessionMediaProperties as _MediaProperties,
    GlobalSystemMediaTransportControlsSessionPlaybackInfo as _PlaybackInfo,
    GlobalSystemMediaTransportControlsSessionTimelineProperties as _TimelineProperties,
)
from winrt.windows.storage.streams import (
    Buffer as _Buffer,
    IBuffer as _IBuffer,
    IRandomAccessStreamReference as _StreamReference,
    IRandomAccessStreamWithContentType as _Stream,
    InputStreamOptions as _InputStreamOptions,
)

# isort: on

from .constants import (
    COVER_FILE,
    COVER_PLACEHOLDER_B64,
    COVER_PLACEHOLDER_RAW,
    MEDIA_DATA_TEMPLATE,
)
from .datastructures import MediaInfo
from .media_session import AbstractMediaSession
from .typing import MediaSessionUpdateCallback
from .utils import async_callback, write_file

logger = logging.getLogger(__name__)


class MediaSessionWindows(AbstractMediaSession):
    """Media controller using Windows.Media.Control"""

    def __init__(
        self,
        callback: Optional[MediaSessionUpdateCallback] = None,
        initial_load: bool = True,
    ) -> None:
        self._update_callback: Optional[MediaSessionUpdateCallback] = callback
        self._manager: _MediaManager | None = None
        self._session: _MediaSession | None = None

        self._data = MEDIA_DATA_TEMPLATE.copy()
        self._data["media_properties"]["thumbnail_data"] = COVER_PLACEHOLDER_B64

        if initial_load:
            asyncio.run(self.load())

    def _update_data(self, key: Any, value: Any) -> None:
        self._data[key] = value
        self._send_data()

    @property
    def data_v1(self) -> dict[str, Any]:
        """Get media session data"""
        return {
            "provider": self._data["provider"],
            "metadata": {
                "title": self._data["media_properties"]["title"],
                "album": self._data["media_properties"]["album_title"],
                "album_artist": self._data["media_properties"]["album_artist"],
                "artist": self._data["media_properties"]["artist"],
                "cover": self._data["media_properties"]["thumbnail"],
                "cover_data": self._data["media_properties"]["thumbnail_data"],
                "duration": self._data["timeline_properties"]["end_time"],
            },
            "status": self._data["playback_info"]["playback_status"],
            "shuffle": self._data["playback_info"]["is_shuffle_active"],
            "position": self._data["timeline_properties"]["position_soft"],
            "loop": self._data["playback_info"].get("auto_repeat_mode"),
        }

    @property
    def data(self) -> MediaInfo:
        return MediaInfo(
            title=self._data["media_properties"]["title"],
            artist=self._data["media_properties"]["artist"],
            album_title=self._data["media_properties"]["album_title"],
            album_artist=self._data["media_properties"]["album_artist"],
            track_number=self._data["media_properties"]["track_number"],
            album_track_count=self._data["media_properties"]["album_track_count"],
            genres=self._data["media_properties"]["genres"],
            cover=self._data["media_properties"]["thumbnail"],
            cover_data=self._data["media_properties"]["thumbnail_data"],
            position=self._data["timeline_properties"]["position_soft"],
            duration=self._data["timeline_properties"]["end_time"],
            state=self._data["playback_info"]["playback_status"],
        )

    @property
    def data_raw(self) -> dict[str, Any]:
        """Get media session data"""
        return self._data

    def _send_data(self) -> None:
        if self._update_callback is None:
            return

        self._update_callback(self.data)

    async def load(self) -> None:
        """Load"""

        self._manager = await _MediaManager.request_async()
        self._manager.add_current_session_changed(async_callback(self._session_events))
        self._manager.add_sessions_changed(async_callback(self._sessions_changed))

        await self._session_events(self._manager)

        self._send_data()

    async def update(self) -> None:
        """Update"""

        self._update_time()

    async def loop(self) -> None:
        """Main loop"""

        if self._manager is None:
            await self.load()

        while True:
            await self.update()
            await asyncio.sleep(0.1)

    def _update_time(self) -> None:
        if not self._session:
            return
        if self._data["playback_info"]["playback_status"] != "playing":
            return
        now = time()

        position: int = self._data["timeline_properties"]["position"]
        last_update: float = self._data["timeline_properties"]["last_updated_time"]
        rate: float = self._data["playback_info"]["playback_rate"]

        if last_update < 0:
            return

        delta_time = now - last_update
        delta_time_mcs = delta_time * 1_000_000
        delta_position = int(rate * delta_time_mcs)

        position_now = position + delta_position

        self._data["timeline_properties"]["position_soft"] = min(
            position_now, self._data["timeline_properties"]["end_time"]
        )

        self._send_data()

    async def _session_events(self, *_: Any) -> None:
        logger.info("Session changed")

        if self._manager is None:
            return

        self._session = self._manager.get_current_session()

        if self._session is None:
            return

        self._update_data("provider", self._session.source_app_user_model_id)

        await self._playback_info_changed()
        await self._timeline_properties_changed()
        await self._media_properties_changed()

        self._session.add_media_properties_changed(
            async_callback(self._media_properties_changed)
        )
        self._session.add_playback_info_changed(
            async_callback(self._playback_info_changed)
        )
        self._session.add_timeline_properties_changed(
            async_callback(self._timeline_properties_changed)
        )

    async def _sessions_changed(self, *_: Any) -> None:
        logger.info("Sessions changed")

        if self._manager is None:
            return

        if (sessions := self._manager.get_sessions()) is None:
            return

        sessions = list(sessions)

        logger.debug("Active sessions count: %s", len(sessions))

    async def _try_load_thumbnail(
        self, stream_ref: _StreamReference | None
    ) -> bytes | None:
        if stream_ref is None:
            logger.debug("Stream reference is None")
            return

        readable_stream: _Stream = await stream_ref.open_read_async()
        thumb_buffer: _IBuffer = _Buffer(readable_stream.size)  # type: ignore

        try:
            await readable_stream.read_async(
                thumb_buffer, thumb_buffer.capacity, _InputStreamOptions.READ_AHEAD
            )

            return bytes(thumb_buffer)

        except OSError as e:
            logger.error("Failed to get thumbnail!\n%s", e)

    async def _media_properties_changed(self, *_: Any) -> None:
        logger.info("Media properties changed")

        if self._session is None:
            return

        try:
            info: _MediaProperties = (
                await self._session.try_get_media_properties_async()
            )
        except PermissionError:
            return

        info_dict: dict[str, Any] = {}
        fields = [
            "album_artist",
            "album_title",
            "album_track_count",
            "artist",
            "subtitle",
            "thumbnail",
            "title",
            "track_number",
            "playback_type",
        ]

        for field in fields:
            try:
                info_dict[field] = getattr(info, field)
            except AttributeError:
                logger.warning("Cannot get attribute '%s'", field)

        info_dict["genres"] = list(info.genres or [])

        thumb_stream_ref: _StreamReference | None = info.thumbnail

        thumb_img: bytes

        thumb = await self._try_load_thumbnail(thumb_stream_ref)

        if thumb:  # (thumb != None) & (thumb != b"")
            thumb_img = thumb
        else:
            if thumb is None:
                logger.warning("Thumbnail is None")
            elif thumb == b"":
                logger.warning("Thumbnail is empty")
            thumb_img = COVER_PLACEHOLDER_RAW
            logger.warning("No correct thumbnail info, using placeholder")

        write_file(COVER_FILE, thumb_img)

        thumbnail_data: str = b64encode(thumb_img).decode("utf-8")

        info_dict["thumbnail_data"] = thumbnail_data

        info_dict["thumbnail"] = COVER_FILE
        info_dict["thumbnail_url"] = "file:///" + COVER_FILE

        logger.debug(pformat(info_dict))
        self._update_data("media_properties", info_dict)

    async def _playback_info_changed(self, *_: Any) -> None:
        logger.info("Playback info changed")

        if self._session is None:
            return

        info: _PlaybackInfo | None = self._session.get_playback_info()

        if info is None:
            return

        info_dict: dict[str, Any] = {}
        fields = (
            "auto_repeat_mode",
            "controls",
            "is_shuffle_active",
            "playback_rate",
            "playback_status",
            "playback_type",
        )
        for field in fields:
            try:
                info_dict[field] = getattr(info, field)
            except AttributeError:
                logger.warning("Cannot get attribute '%s'", field)
        status_codes = {
            0: "closed",
            1: "opened",
            2: "changing",
            3: "stopped",
            4: "playing",
            5: "paused",
        }
        repeat_codes = {
            0: "none",
            1: "track",
            2: "all",
        }
        info_dict["playback_status"] = status_codes[int(info_dict["playback_status"])]
        if (repeat_mode := info_dict.get("auto_repeat_mode")) is not None:
            info_dict["auto_repeat_mode"] = repeat_codes[int(repeat_mode)]
        info_dict["controls"] = None
        logger.debug(pformat(info_dict))
        self._update_data("playback_info", info_dict)

    async def _timeline_properties_changed(self, *_: Any) -> None:
        logger.info("Timeline properties changed")

        if not self._session:
            return

        info: _TimelineProperties | None = self._session.get_timeline_properties()

        if info is None:
            return

        info_dict: dict[str, Any] = {}

        fields = (
            "end_time",
            "last_updated_time",
            "max_seek_time",
            "min_seek_time",
            "position",
            "start_time",
        )

        for field in fields:
            try:
                info_dict[field] = getattr(info, field)
            except AttributeError:
                logger.warning("Cannot get attribute '%s'", field)

        for f in (
            "end_time",
            "max_seek_time",
            "min_seek_time",
            "position",
            "start_time",
        ):
            k: timedelta = info_dict[f]
            info_dict[f] = int(k.microseconds + k.seconds * 1e6)

        info_dict["last_updated_time"] = info.last_updated_time.timestamp()
        info_dict["position_soft"] = info_dict["position"]
        logger.debug(pformat(info_dict))
        self._update_data("timeline_properties", info_dict)

    #
    # PUBLIC METHODS
    #

    @final
    async def play(self) -> None:
        """Start playback"""

        if self._session is not None:
            await self._session.try_play_async()

    @final
    async def stop(self) -> None:
        """Stop playback"""

        if self._session is not None:
            await self._session.try_stop_async()

    @final
    async def pause(self) -> None:
        """Pause playback"""

        if self._session is not None:
            await self._session.try_pause_async()

    @final
    async def set_position(self, position: float) -> None:
        """Set position in seconds"""

        if self._session is not None:
            await self._session.try_change_playback_position_async(int(position * 1e7))

    @final
    async def play_pause(self) -> None:
        """Toggle play/pause"""

        if self._session is not None:
            await self._session.try_toggle_play_pause_async()

    @final
    async def next(self) -> None:
        """Select next track"""

        if self._session is not None:
            await self._session.try_skip_next_async()

    @final
    async def prev(self) -> None:
        """Select previous track"""

        if self._session is not None:
            await self._session.try_skip_previous_async()

    previous = prev

    async def set_repeat(self, mode: str | int | MediaRepeatMode) -> None:
        """Set repeat mode

        Available modes: 'none', 'track', 'list'"""

        if self._session is None:
            return

        _mode: MediaRepeatMode
        if isinstance(mode, str):
            _mode = {
                "none": MediaRepeatMode.NONE,
                "track": MediaRepeatMode.TRACK,
                "list": MediaRepeatMode.LIST,
            }.get(mode, MediaRepeatMode.NONE)
        elif isinstance(mode, int):  # type: ignore
            _mode = MediaRepeatMode(mode)
        else:
            _mode = mode

        await self._session.try_change_auto_repeat_mode_async(_mode)

    @final
    async def set_shuffle(self, shuffle: bool) -> None:
        """shuffle: True, False"""

        if self._session is not None:
            await self._session.try_change_shuffle_active_async(shuffle)

    @final
    async def toggle_repeat(self) -> None:
        """Toggle repeat (none, track, list)"""

        if self._session is None:
            return
        if (playback_info := self._session.get_playback_info()) is None:
            return
        if (repeat := playback_info.auto_repeat_mode) is None:
            return
        _mode = MediaRepeatMode((repeat + 1) % 3)
        await self._session.try_change_auto_repeat_mode_async(_mode)

    @final
    async def toggle_shuffle(self) -> None:
        """Toggle shuffle (on, off)"""

        if self._session is None:
            return
        if (playback_info := self._session.get_playback_info()) is None:
            return
        if (shuffle := playback_info.is_shuffle_active) is None:
            return
        await self._session.try_change_shuffle_active_async(not shuffle)

    @final
    async def seek_percentage(self, percentage: int | float) -> None:
        """Seek to percentage in range [0, 100]"""

        if self._session is None:
            return
        if (timeline_properties := self._session.get_timeline_properties()) is None:
            return

        duration = timeline_properties.max_seek_time

        position = int(duration.total_seconds() * percentage / 100)
        await self.set_position(position)

    @final
    async def rewind(self) -> None:
        """Idk what it is"""

        if self._session is None:
            return
        await self._session.try_rewind_async()
