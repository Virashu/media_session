"""
Media Control API
"""

__all__ = ["AbstractMediaSession"]

import abc

from .datastructures import MediaInfo
from .typing import MediaSessionUpdateCallback


class MediaControlInterface(abc.ABC):
    """Media Control Interface

    Defines methods for control of playback by user
    """

    @abc.abstractmethod
    async def play(self) -> None: ...

    @abc.abstractmethod
    async def pause(self) -> None: ...

    @abc.abstractmethod
    async def play_pause(self) -> None: ...

    @abc.abstractmethod
    async def next(self) -> None: ...

    @abc.abstractmethod
    async def prev(self) -> None: ...

    @abc.abstractmethod
    async def stop(self) -> None: ...

    @abc.abstractmethod
    async def seek_percentage(self, percentage: float) -> None: ...


class AbstractMediaSession(MediaControlInterface):
    """Base controller"""

    @abc.abstractmethod
    def __init__(
        self, callback: MediaSessionUpdateCallback, initial_load: bool = True
    ) -> None: ...

    @abc.abstractmethod
    async def load(self) -> None: ...

    @abc.abstractmethod
    async def update(self) -> None: ...

    @property
    @abc.abstractmethod
    def data(self) -> MediaInfo: ...
