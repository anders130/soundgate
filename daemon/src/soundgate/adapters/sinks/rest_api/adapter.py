import os

import uvicorn

from ....application.ports.outbound import SourceControlPort
from ....application.use_cases.process_event import ProcessEventUseCase
from ....application.use_cases.query_state import QueryStateUseCase
from .app import build_app


class RestApiAdapter:
    def __init__(
        self,
        query: QueryStateUseCase,
        process: ProcessEventUseCase,
        control_map: dict[str, SourceControlPort],
        port: int = 7676,
    ) -> None:
        self._app = build_app(query, process, control_map)
        self._port = port

    @classmethod
    def from_env(
        cls,
        query: QueryStateUseCase,
        process: ProcessEventUseCase,
        control_map: dict[str, SourceControlPort],
    ) -> "RestApiAdapter":
        return cls(
            query=query,
            process=process,
            control_map=control_map,
            port=int(os.environ.get("SOUNDGATE_HTTP_PORT", "7676")),
        )

    async def run(self) -> None:
        config = uvicorn.Config(
            self._app,
            host="0.0.0.0",
            port=self._port,
            log_level="warning",
            loop="asyncio",
        )
        await uvicorn.Server(config).serve()
