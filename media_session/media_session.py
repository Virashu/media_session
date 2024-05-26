"""
Media Control API
"""

__all__ = ["BaseMediaSession"]

import abc

from .datastructures import MediaInfo
from .typing import MediaSessionUpdateCallback


class MediaControlInterface(abc.ABC):
    """Media Control Interface"""

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


class BaseMediaSession(MediaControlInterface):
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
    async def data(self) -> MediaInfo: ...
