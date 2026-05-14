import asyncio
from datetime import datetime, timezone

from ...domain.aggregator import AggregatorService
from ...domain.events import PlayerEvent
from ...domain.source import Source
from ..ports.outbound import StateExportPort, VolumePort
from ..snapshot import Snapshot


class ProcessEventUseCase:
    def __init__(
        self,
        sources: dict[str, Source],
        aggregator: AggregatorService,
        priority_map: dict[str, int],
        volume_port: VolumePort,
        initial_volume: float = 1.0,
    ) -> None:
        self.sources = sources
        self._aggregator = aggregator
        self._priority_map = priority_map
        self._volume_port = volume_port
        self._volume: float = initial_volume
        self._sinks: list[StateExportPort] = []

    def register_sink(self, sink: StateExportPort) -> None:
        self._sinks.append(sink)

    async def handle_event(self, event: PlayerEvent) -> None:
        if event.volume is not None:
            self._volume = event.volume
            await self._volume_port.set_volume(event.volume)

        name = event.source
        if name not in self.sources:
            priority = self._priority_map.get(name, len(self._priority_map))
            self.sources[name] = Source(name=name, priority=priority)
        source = self.sources[name]

        now = datetime.now(timezone.utc)
        if event.state is not None:
            self._aggregator.apply_state(source, event.state, now)
        else:
            self._aggregator.touch(source, now)

        if event.metadata is not None:
            source.metadata = event.metadata

        if event.position_us is not None:
            source.position_us = event.position_us

        await self._publish()

    @property
    def volume(self) -> float:
        return self._volume

    async def set_volume(self, level: float) -> None:
        self._volume = max(0.0, min(1.0, level))
        await self._volume_port.set_volume(self._volume)
        await self._publish()

    async def tick(self) -> None:
        await self._publish()

    async def _publish(self) -> None:
        now = datetime.now(timezone.utc)
        active = self._aggregator.active_source(self.sources, now)
        snapshot = Snapshot(active=active, volume=self._volume)
        await asyncio.gather(*(sink.publish(snapshot) for sink in self._sinks))
