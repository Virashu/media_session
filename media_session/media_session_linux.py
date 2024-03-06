from .media_session import BaseMediaSession
import dbus

class MediaSessionLinux(BaseMediaSession): ...

bus = dbus.SessionBus()
proxy = bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
properties_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
properties_manager.Set('org.mpris.MediaPlayer2.Player', 'Volume', 100.0)
curr_volume = properties_manager.Get('org.mpris.MediaPlayer2.Player', 'Volume')