"""
Media controller using MPRIS
"""

__all__ = ["MediaSessionLinux"]

from typing import Any, overload

import dbus

from .datastructures import MediaInfo
from .media_session import BaseMediaSession
from .typing import MediaSessionUpdateCallback


@overload
def dbus_to_py(dbus_obj: dbus.Dictionary) -> dict: ...


@overload
def dbus_to_py(dbus_obj: dbus.Array) -> list: ...


def dbus_to_py(dbus_obj: Any) -> object:
    if isinstance(dbus_obj, dbus.Array):
        return list(map(dbus_to_py, dbus_obj))
    elif isinstance(dbus_obj, dbus.Dictionary):
        return {dbus_to_py(k): dbus_to_py(v) for k, v in dbus_obj.items()}
    elif isinstance(dbus_obj, dbus.String):
        return str(dbus_obj)
    elif isinstance(dbus_obj, (dbus.Int16, dbus.Int32, dbus.Int64)):
        return int(dbus_obj)
    elif isinstance(dbus_obj, dbus.ObjectPath):
        return str(dbus_obj)
    else:
        return dbus_obj


class MediaSessionLinux(BaseMediaSession):
    def __init__(self, callback: MediaSessionUpdateCallback) -> None:
        self._update_callback = callback
        self._bus = dbus.SessionBus()

        names = self._bus.list_names()

        if not names:
            return

        players = tuple(
            filter(lambda x: x.startswith("org.mpris.MediaPlayer2."), names)
        )

        if len(players) == 0:
            print("No players found")
            return

        if len(players) == 1:
            index = 0
        else:
            print("Found multiple players\n================")
            print(*players, sep="\n")
            index = int(input("Index: "))

        selected = players[index]

        print(selected)

        proxy = self._bus.get_object(str(selected), "/org/mpris/MediaPlayer2")

        properties_manager = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
        metadata: dbus.Dictionary = properties_manager.Get(
            "org.mpris.MediaPlayer2.Player", "Metadata"
        )
        self._data_raw: dict = dbus_to_py(metadata)

    async def load(self) -> None: ...

    @property
    async def data(self) -> MediaInfo:
        return MediaInfo(
            title=self._data_raw.get("xesam:title"),
            artist=self._data_raw["xesam:artist"],
            album_title=self._data_raw["xesam:album"],
            album_artist=self._data_raw["xesam:albumArtist"],
            track_number=self._data_raw["xesam:trackNumber"],
            album_track_count=self._data_raw["xesam:discNumber"],
            genres=self._data_raw["xesam:genre"],
            thumbnail=self._data_raw["mpris:artUrl"],
            thumbnail_data="",
        )

    async def update(self) -> None:
        pass

    async def loop(self) -> None:
        self._update_callback(await self.data)

    async def play(self) -> None:
        pass

    async def pause(self) -> None:
        pass

    async def play_pause(self) -> None:
        pass

    async def next(self) -> None:
        pass

    async def prev(self) -> None:
        pass

    async def stop(self) -> None:
        pass
