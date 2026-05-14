from dataclasses import dataclass
from enum import StrEnum

type SourceName = str


class PlaybackState(StrEnum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass(frozen=True)
class Metadata:
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    art_url: str | None = None
    duration_us: int | None = None
    track_id: str | None = None


@dataclass(frozen=True)
class PlayerEvent:
    source: SourceName
    state: PlaybackState | None = None
    metadata: Metadata | None = None
    volume: float | None = None
    position_us: int | None = None
