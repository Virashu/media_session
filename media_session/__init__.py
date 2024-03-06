"""
MediaSessionAPI for client

Made using 'winrt' python mapping
"""

__all__ = ["MediaSession"]
import os

if os.name == "nt":
    from .media_session_windows import MediaSessionWindows as MediaSession
elif os.name == "posix":
    from .media_session_linux import MediaSessionLinux as MediaSession
else:
    raise OSError("Unsupported platform")
