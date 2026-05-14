from dataclasses import dataclass, field
from datetime import datetime

from .events import Metadata, PlaybackState, SourceName


@dataclass
class Source:
    name: SourceName
    priority: int
    state: PlaybackState = PlaybackState.STOPPED
    metadata: Metadata = field(default_factory=Metadata)
    position_us: int = 0
    last_playing_at: datetime | None = None
    last_event_at: datetime | None = None
