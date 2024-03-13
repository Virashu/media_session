"""
Media controller using MPRIS
"""

# from media_session import BaseMediaSession
import dbus

# class MediaSessionLinux(BaseMediaSession): ...

bus = dbus.SessionBus()


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
