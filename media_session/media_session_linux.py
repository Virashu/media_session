# from media_session import BaseMediaSession
import re
import dbus

# class MediaSessionLinux(BaseMediaSession): ...

bus = dbus.SessionBus()


"""
dbus-send --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2> /dev/null | sed -r -n '/org.mpris.MediaPlayer2/{s@.*org.mpris.MediaPlayer2.([^"]+).*@\1@g;p}'
"""

def main():

    names = bus.list_names()

    if not names:
        return

    players = tuple(filter(lambda x: x.startswith("org.mpris.MediaPlayer2."), names))
    print(*players, sep="\n")

    index = int(input("Index: "))

    selected = players[index]

    print(selected)

    proxy = bus.get_object(str(selected), "/org/mpris/MediaPlayer2")

    properties_manager = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
    metadata = properties_manager.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    print(metadata)

main()

