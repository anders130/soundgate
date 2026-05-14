from __future__ import annotations

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
_log = logging.getLogger(__name__)


async def main() -> None:
    _log.info("soundgate starting")


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
