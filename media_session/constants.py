import json
from typing import Any
from base64 import b64encode


from .utils import read_file, read_file_bytes

DIRNAME = __file__.replace("\\", "/").rsplit("/", 1)[0]

MEDIA_DATA_TEMPLATE: dict[str, Any] = json.loads(
    read_file(f"{DIRNAME}/static/template.json")
)
COVER_FILE: str = f"{DIRNAME}/static/media_thumb.png"
COVER_PLACEHOLDER_FILE: str = f"{DIRNAME}/static/placeholder.png"
COVER_PLACEHOLDER_RAW: bytes = read_file_bytes(COVER_PLACEHOLDER_FILE)
COVER_PLACEHOLDER_B64: str = b64encode(COVER_PLACEHOLDER_RAW).decode("utf-8")
