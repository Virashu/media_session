"""
MediaSessionAPI for client

Made using 'winrt' python mapping
"""

__all__ = ["AbstractMediaSession", "MediaSession"]
import sys

from .media_session import AbstractMediaSession

if sys.platform == "win32":
    from .media_session_windows import MediaSessionWindows as MediaSession
elif sys.platform == "linux":
    from .media_session_linux import MediaSessionLinux as MediaSession
else:
    raise OSError("Unsupported platform")
