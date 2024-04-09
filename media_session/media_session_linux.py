"""
Media controller using MPRIS
"""

import dbus
from pprint import pprint
from typing import Any, Callable


def dbus_to_py(dbus_obj: Any) -> Any:
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


bus = dbus.SessionBus()


def main():
    names = bus.list_names()

    if not names:
        return

    players = tuple(filter(lambda x: x.startswith("org.mpris.MediaPlayer2."), names))

    if len(players) == 0:
        print("No players found")
        return

    if len(players) == 1:
        index = 0
    else:
        print(*players, sep="\n")
        index = int(input("Index: "))

    selected = players[index]

    print(selected)

    proxy = bus.get_object(str(selected), "/org/mpris/MediaPlayer2")

    properties_manager = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
    metadata = properties_manager.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    pprint(dbus_to_py(metadata))


main()

#  'mpris:artUrl': '/home/virashu/.config//musikcube/1//thumbs/482.jpg',
#  'mpris:length': 229000000,
#  'mpris:trackid': '/1',
#  'xesam:album': '',
#  'xesam:albumArtist': ['Azu Izumi 2'],
#  'xesam:artist': ['Azu Izumi 2'],
#  'xesam:comment': [''],
#  'xesam:discNumber': 1,
#  'xesam:genre': ['Dance & EDM'],
#  'xesam:title': 'REOL - drop pop candy (OKINAWA IKITAI remix)',
#  'xesam:trackNumber': 1

from .media_session import BaseMediaSession
from .typing import MediaSessionUpdateCallback


class MediaSessionLinux(BaseMediaSession):
    def __init__(self, callback: MediaSessionUpdateCallback) -> None: ...

    async def play(self) -> None:
        pass

    def pause(self) -> None:
        pass

    def play_pause(self) -> None:
        pass

    def next(self) -> None:
        pass

    def prev(self) -> None:
        pass

    def stop(self) -> None:
        pass
