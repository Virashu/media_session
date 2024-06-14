# Media Session API


## Todo

- [x] Windows `Windows.Media.Control` support
- [ ] Linux `MPRIS` support
- [ ] Client application side API (get info, controls)
- [ ] Player application side API (set playback info, handle controls)
- [ ] Get rid of side effects (file writing, etc)
- [ ] Turn constants into custom params
- [ ] Check if controls is supported before execution
- [ ] Logging

## Data structures (json)

```
<MediaInfo> {
  title: string
  artist: string

  album_title: string
  album_artist: string

  album_track_count: number
  track_number: number

  genres: string[]

  cover: string
  cover_data: string
}
```