from __future__ import annotations

import asyncio
import logging
import os

from .adapters.sinks.pipewire_volume import PipewireVolumeAdapter
from .adapters.sinks.rest_api.adapter import RestApiAdapter
from .adapters.sources.bluetooth import BluetoothAdapter
from .adapters.sources.librespot import LibrespotAdapter
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
    bluetooth = BluetoothAdapter(process)
    librespot = LibrespotAdapter.from_env(process)
    rest_api = RestApiAdapter.from_env(
        query=query,
        process=process,
        control_map={"bluetooth": bluetooth},
    )

    await asyncio.gather(bluetooth.run(), librespot.run(), rest_api.run())


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
