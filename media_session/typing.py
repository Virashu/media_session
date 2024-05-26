"""Internal types"""

__all__ = ["MediaSessionUpdateCallback"]

from typing import Any, Callable, TypeAlias

from media_session.datastructures import MediaInfo

MediaSessionUpdateCallback: TypeAlias = Callable[[MediaInfo], Any]
