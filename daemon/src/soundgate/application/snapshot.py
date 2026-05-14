from dataclasses import dataclass

from ..domain.source import Source


@dataclass(frozen=True)
class Snapshot:
    active: Source | None
    volume: float
