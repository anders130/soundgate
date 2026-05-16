from __future__ import annotations

import asyncio
import logging
import os

from .adapters.sinks.alsa_volume import AlsaVolumeAdapter
from .adapters.sinks.pipewire_volume import PipewireVolumeAdapter
from .adapters.sinks.rest_api.adapter import RestApiAdapter
from .adapters.sources.bluetooth import BluetoothAdapter
from .adapters.sources.spotifyd import SpotifydAdapter
from .application.use_cases.process_event import ProcessEventUseCase
from .application.use_cases.query_state import QueryStateUseCase
from .domain.aggregator import AggregatorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
_log = logging.getLogger(__name__)

_PRIORITY_MAP = {"bluetooth": 0, "spotify": 1}


async def main() -> None:
    _log.info("soundgate starting")

    inactivity_timeout = int(os.environ.get("SOUNDGATE_INACTIVITY_TIMEOUT", "10"))

    sources: dict = {}
    aggregator = AggregatorService(inactivity_timeout=inactivity_timeout)
    volume_adapter = PipewireVolumeAdapter.from_env()
    saved_volume = await volume_adapter.restore_saved()

    process = ProcessEventUseCase(
        sources=sources,
        aggregator=aggregator,
        priority_map=_PRIORITY_MAP,
        volume_port=volume_adapter,
        initial_volume=saved_volume if saved_volume is not None else 1.0,
    )

    query = QueryStateUseCase(sources=sources, aggregator=aggregator)
    bluetooth = BluetoothAdapter(process, volume_provider=lambda: process.volume)
    process.register_volume_feedback(bluetooth)
    alsa_volume = AlsaVolumeAdapter.from_env()
    if alsa_volume is not None:
        process.register_volume_feedback(alsa_volume)

    async def _restore_alsa_volume() -> None:
        if alsa_volume is not None:
            await alsa_volume.sync_volume(process.volume)

    spotifyd = SpotifydAdapter.from_env(
        process,
        on_init_suppressed=_restore_alsa_volume if alsa_volume is not None else None,
    )
    rest_api = RestApiAdapter.from_env(
        query=query,
        process=process,
        control_map={"bluetooth": bluetooth},
    )

    await asyncio.gather(bluetooth.run(), spotifyd.run(), rest_api.run())


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
