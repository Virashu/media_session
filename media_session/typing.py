"""Internal types"""

__all__ = ["MediaSessionUpdateCallback"]

from typing import Any, Callable, TypeAlias


MediaSessionUpdateCallback: TypeAlias = Callable[[dict[str, Any]], Any]
