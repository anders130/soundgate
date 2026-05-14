from typing import Protocol

from ...domain.events import PlayerEvent


class PlayerEventPort(Protocol):
    async def handle_event(self, event: PlayerEvent) -> None: ...
