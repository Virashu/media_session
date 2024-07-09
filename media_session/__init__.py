"""
MediaSessionAPI for client

Made using 'winrt' python mapping
"""

__all__ = ["AbstractMediaSession", "MediaSession"]
import os

from .media_session import BaseMediaSession as AbstractMediaSession

if os.name == "nt":
    from .media_session_windows import MediaSessionWindows as MediaSession
elif os.name == "posix":
    from .media_session_linux import MediaSessionLinux as MediaSession
else:
    raise OSError("Unsupported platform")
