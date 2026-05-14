from datetime import datetime, timezone

from ...domain.aggregator import AggregatorService
from ...domain.source import Source


class QueryStateUseCase:
    def __init__(
        self, sources: dict[str, Source], aggregator: AggregatorService
    ) -> None:
        self._sources = sources
        self._aggregator = aggregator

    def active_source(self) -> Source | None:
        return self._aggregator.active_source(self._sources, datetime.now(timezone.utc))

    def all_sources(self) -> dict[str, Source]:
        return dict(self._sources)
