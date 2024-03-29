"""
Media Control API
"""

__all__ = ["BaseMediaSession"]

import abc


class BaseMediaSession(abc.ABC):
    """Base controller"""

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
