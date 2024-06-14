import asyncio
import json

from media_session.datastructures import MediaInfo

from . import MediaSession
from .utils import write_file

# DIRNAME = __file__.replace("\\", "/").rsplit("/", 1)[0]  # this file path
INFODIR = "info.json"  # cwd


def _update(data: MediaInfo):
    write_file(INFODIR, json.dumps(data.as_dict(), indent="  "))


def main():

    _ms = MediaSession(callback=_update)

    try:
        asyncio.run(_ms.loop())
    except KeyboardInterrupt:
        pass
